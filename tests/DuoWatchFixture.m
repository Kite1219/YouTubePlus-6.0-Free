#import <UIKit/UIKit.h>
#import <objc/runtime.h>
extern BOOL TPDuoEligible(CGSize,UIEdgeInsets,BOOL,BOOL,BOOL);
extern BOOL TPInstallDuoWatchLayout(void);
@interface TPFixtureWindow : UIWindow
@property UIEdgeInsets testInsets;
@end
@implementation TPFixtureWindow
- (UIEdgeInsets)safeAreaInsets { return self.testInsets; }
@end

// Surrogate host exercises the production hook on actual UIKit objects.
// It is not YouTube and does not establish physical Duo rendering.
@interface YTWatchView : UIView {
@public BOOL _watchNextExtendsToScreenEdgeEnabled;
@public BOOL _engagementPanelExtendsToScreenEdgeEnabled;
}
@property BOOL fullscreen;
@property NSInteger layoutCalls;
@property UIView *feed;
@property UIView *panel;
- (BOOL)isFullscreen;
@end
@implementation YTWatchView
- (instancetype)initWithFrame:(CGRect)frame {
    if((self=[super initWithFrame:frame])){
        self.feed=[UIView new];self.panel=[UIView new];[self addSubview:self.feed];[self addSubview:self.panel];
    }return self;
}
- (BOOL)isFullscreen {return self.fullscreen;}
- (void)layoutSubviews {
    [super layoutSubviews];self.layoutCalls++;
    CGFloat reserved=self.window.safeAreaInsets.right;
    self.feed.frame=CGRectMake(550,0,self.bounds.size.width-550-reserved+(_watchNextExtendsToScreenEdgeEnabled?reserved:0),self.bounds.size.height);
    self.panel.frame=CGRectMake(550,0,self.bounds.size.width-550-reserved+(_engagementPanelExtendsToScreenEdgeEnabled?reserved:0),self.bounds.size.height);
}
@end

@interface FixtureApp : UIResponder <UIApplicationDelegate>
@property (nonatomic,strong) TPFixtureWindow *window;
@end
@implementation FixtureApp
- (BOOL)application:(UIApplication*)app didFinishLaunchingWithOptions:(NSDictionary*)options {
    self.window=[[TPFixtureWindow alloc]initWithFrame:CGRectMake(0,0,951,669)];
    self.window.rootViewController=[UIViewController new];[self.window makeKeyAndVisible];
    dispatch_async(dispatch_get_main_queue(),^{ [self runChecks]; });return YES;
}
- (void)runChecks {
    NSMutableArray *results=[NSMutableArray new];
    void(^check)(BOOL,NSString*)=^(BOOL ok,NSString *name){[results addObject:@{@"name":name,@"passed":@(ok)}];};
    UIEdgeInsets safe=UIEdgeInsetsMake(0,0,0,84);
    check(TPDuoEligible(CGSizeMake(951,669),safe,YES,NO,NO),@"large landscape phone eligible");
    check(!TPDuoEligible(CGSizeMake(844,390),safe,YES,NO,NO),@"ordinary landscape phone unchanged");
    check(!TPDuoEligible(CGSizeMake(951,669),safe,NO,NO,NO),@"iPad unchanged");
    check(!TPDuoEligible(CGSizeMake(669,951),safe,YES,NO,NO),@"portrait unchanged");
    check(!TPDuoEligible(CGSizeMake(951,669),safe,YES,YES,NO),@"fullscreen unchanged");
    check(!TPDuoEligible(CGSizeMake(951,669),UIEdgeInsetsZero,YES,NO,NO),@"no reserved strip unchanged");
    check(!TPDuoEligible(CGSizeMake(951,669),safe,YES,NO,YES),@"RTL unsupported geometry unchanged");
    check(TPInstallDuoWatchLayout(),@"exact host hook installed");
    self.window.bounds=CGRectMake(0,0,951,669);self.window.testInsets=safe;
    YTWatchView *watch=[[YTWatchView alloc]initWithFrame:self.window.bounds];
    [self.window.rootViewController.view addSubview:watch];
    [watch layoutSubviews];
    check(watch->_watchNextExtendsToScreenEdgeEnabled && watch->_engagementPanelExtendsToScreenEdgeEnabled,@"both native edge extension paths enabled");
    check(fabs(CGRectGetMaxX(watch.feed.frame)-951)<0.5 && fabs(CGRectGetMaxX(watch.panel.frame)-951)<0.5,@"feed and panel extend to window edge");
    check(UIEdgeInsetsEqualToEdgeInsets(self.window.safeAreaInsets,safe),@"system safe-area information preserved");
    NSInteger calls=watch.layoutCalls;[watch layoutSubviews];
    check(watch.layoutCalls==calls+1,@"one original layout call without recursion");
    watch.fullscreen=YES;[watch layoutSubviews];
    check(!watch->_watchNextExtendsToScreenEdgeEnabled && !watch->_engagementPanelExtendsToScreenEdgeEnabled,@"original flags restored for fullscreen");
    watch.fullscreen=NO;[watch layoutSubviews];watch.hidden=YES;[watch layoutSubviews];
    check(!watch->_watchNextExtendsToScreenEdgeEnabled,@"hidden preview state restored");
    watch.hidden=NO;self.window.testInsets=UIEdgeInsetsZero;[watch layoutSubviews];
    check(!watch->_watchNextExtendsToScreenEdgeEnabled,@"rotation without side inset restores flags");
    self.window.testInsets=safe;watch.frame=CGRectMake(0,0,300,200);[watch layoutSubviews];
    check(!watch->_watchNextExtendsToScreenEdgeEnabled,@"miniplayer unchanged");
    watch.frame=self.window.bounds;watch.transform=CGAffineTransformMakeScale(0.3,0.3);[watch layoutSubviews];
    check(!watch->_watchNextExtendsToScreenEdgeEnabled,@"scaled transition view unchanged");watch.transform=CGAffineTransformIdentity;
    watch.frame=self.window.bounds;watch->_watchNextExtendsToScreenEdgeEnabled=YES;[watch layoutSubviews];watch.fullscreen=YES;[watch layoutSubviews];
    check(watch->_watchNextExtendsToScreenEdgeEnabled && !watch->_engagementPanelExtendsToScreenEdgeEnabled,@"preexisting native flag choices preserved");
    BOOL passed=YES;for(NSDictionary *r in results)if(![r[@"passed"]boolValue])passed=NO;
    NSDictionary *report=@{@"passed":@(passed),@"checks":results,@"fixtureOnly":@YES,@"physicalDeviceTested":@NO};
    NSData *data=[NSJSONSerialization dataWithJSONObject:report options:NSJSONWritingPrettyPrinted error:nil];
    NSString *file=[NSSearchPathForDirectoriesInDomains(NSDocumentDirectory,NSUserDomainMask,YES).firstObject stringByAppendingPathComponent:@"fixture.json"];
    [data writeToFile:file atomically:YES];NSLog(@"FIXTURE %@",passed?@"PASS":@"FAIL");exit(passed?0:1);
}
@end
int main(int argc,char**argv){@autoreleasepool{return UIApplicationMain(argc,argv,nil,NSStringFromClass(FixtureApp.class));}}
