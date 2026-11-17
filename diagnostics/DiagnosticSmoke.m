#import <UIKit/UIKit.h>
#import <QuartzCore/QuartzCore.h>
#include <math.h>
extern NSDictionary *TPCollectDiagnostics(UIWindow *);
extern NSData *TPDiagnosticsJSON(NSDictionary *);
extern void TPShowDiagnosticButton(void);

@interface YTWatchView : UIView {
@public UIView *_watchNextWrapperView;
@public UIView *_engagementPanelView;
}
- (BOOL)isFullscreen;
- (UIEdgeInsets)watchNextSafeAreaInsets;
@end
@implementation YTWatchView
- (BOOL)isFullscreen{return NO;}
- (UIEdgeInsets)watchNextSafeAreaInsets{return self.safeAreaInsets;}
@end

@interface SmokeScene : UIResponder <UIWindowSceneDelegate>
@property(nonatomic,strong) UIWindow *window;
@property BOOL tested;
@end
@implementation SmokeScene
- (void)scene:(UIScene *)scene willConnectToSession:(UISceneSession *)session options:(UISceneConnectionOptions *)options {
    self.window=[[UIWindow alloc]initWithWindowScene:(UIWindowScene *)scene];
    self.window.rootViewController=[UIViewController new];self.window.rootViewController.view.backgroundColor=UIColor.systemBackgroundColor;
    [self.window makeKeyAndVisible];
}
- (void)sceneDidBecomeActive:(UIScene *)scene {
    if(self.tested)return;self.tested=YES;dispatch_async(dispatch_get_main_queue(),^{[self test];});
}
- (void)test {
    UIView *root=self.window.rootViewController.view;
    YTWatchView *watch=[[YTWatchView alloc]initWithFrame:root.bounds];watch.autoresizingMask=UIViewAutoresizingFlexibleWidth|UIViewAutoresizingFlexibleHeight;[root addSubview:watch];
    UIView *panel=[[UIView alloc]initWithFrame:CGRectMake(root.bounds.size.width*.6,0,root.bounds.size.width*.3,root.bounds.size.height)];panel.backgroundColor=UIColor.darkGrayColor;panel.clipsToBounds=YES;[watch addSubview:panel];watch->_watchNextWrapperView=panel;watch->_engagementPanelView=panel;
    CALayer *mask=[CALayer layer];mask.frame=panel.bounds;mask.backgroundColor=UIColor.blackColor.CGColor;panel.layer.mask=mask;
    UILabel *label=[UILabel new];label.text=@"PRIVATE_TEXT_SENTINEL_7194";label.accessibilityIdentifier=@"PRIVATE_ID_SENTINEL_7194";label.frame=CGRectMake(4,4,200,30);[watch addSubview:label];
    [NSUserDefaults.standardUserDefaults setObject:@"PRIVATE_TOKEN_SENTINEL_7194" forKey:@"authToken"];
    [NSUserDefaults.standardUserDefaults setObject:@"PRIVATE_LAYOUT_SENTINEL_7194" forKey:@"layoutSecret"];
    [NSUserDefaults.standardUserDefaults setObject:@1234567890 forKey:@"phoneNumber"];
    NSLayoutConstraint *height=[label.heightAnchor constraintEqualToConstant:30];height.active=YES;
    CGRect original=watch.frame;UIEdgeInsets safe=watch.safeAreaInsets;
    TPShowDiagnosticButton();
    [watch layoutSubviews];
    UIButton *button=nil;for(UIView *v in self.window.subviews)if([NSStringFromClass(v.class)isEqualToString:@"TPDiagButton"])button=(id)v;
    [button sendActionsForControlEvents:UIControlEventTouchUpInside];
    dispatch_after(dispatch_time(DISPATCH_TIME_NOW,NSEC_PER_SEC),dispatch_get_main_queue(),^{
        NSMutableArray *checks=[NSMutableArray new];void(^check)(BOOL,NSString*)=^(BOOL ok,NSString *name){[checks addObject:@{@"name":name,@"passed":@(ok)}];NSLog(@"CHECK %@ %@",ok?@"PASS":@"FAIL",name);};
        NSString *copied=UIPasteboard.generalPasteboard.string ?: @"";
        NSRange newline=[copied rangeOfString:@"\n"];NSDictionary *report=newline.location==NSNotFound?nil:[NSJSONSerialization JSONObjectWithData:[[copied substringFromIndex:newline.location+1]dataUsingEncoding:NSUTF8StringEncoding] options:0 error:nil];
        check(button!=nil,@"Copy diagnostics button attached to the actual scene window");
        check([copied hasPrefix:@"YouTubePlus Layout Diagnostics 1\n"]&&report!=nil,@"one button action copies valid diagnostic JSON");
        check([report[@"views"]count]>2,@"window association does not prune the complete view tree");
        check([report[@"roles"]count]>0,@"watch wrapper and engagement panel roles captured");
        check([report[@"constraints"]count]>0,@"active Auto Layout constraints captured");
        BOOL maskFound=NO;for(NSDictionary *v in report[@"views"])if(v[@"mask"])maskFound=YES;
        check(maskFound,@"ancestor clipping and layer masks captured");
        check([report[@"images"]count]>0,@"loaded-image SDK and library data captured");
        check([report[@"windows"]count]>0,@"actual window and screen coordinate records captured");
        check([report[@"layoutObservers"][@"layoutSubviews"][@"calls"]unsignedIntegerValue]>0,@"read-only layout observer forwards and counts native layout calls");
        check(![copied containsString:@"PRIVATE_"],@"view text, accessibility IDs and credential-like preferences excluded");
        check(CGRectEqualToRect(original,watch.frame)&&UIEdgeInsetsEqualToEdgeInsets(safe,watch.safeAreaInsets)&&height.active,@"collector does not change original geometry, safe areas or constraints");
        NSData *sanitized=TPDiagnosticsJSON(@{@"value":@(NAN)});NSDictionary *decoded=sanitized?[NSJSONSerialization JSONObjectWithData:sanitized options:0 error:nil]:nil;
        check(decoded[@"value"]==NSNull.null,@"nonfinite geometry is safely serialized as null");
        BOOL passed=YES;for(NSDictionary *c in checks)if(![c[@"passed"]boolValue])passed=NO;
        NSDictionary *result=@{@"passed":@(passed),@"checks":checks,@"fullYouTubeTest":@NO,@"windowBounds":NSStringFromCGRect(self.window.bounds),@"deviceClass":UIDevice.currentDevice.model,@"reportBytes":@([copied lengthOfBytesUsingEncoding:NSUTF8StringEncoding])};
        NSString *path=[NSSearchPathForDirectoriesInDomains(NSDocumentDirectory,NSUserDomainMask,YES).firstObject stringByAppendingPathComponent:@"smoke.json"];
        [TPDiagnosticsJSON(result)writeToFile:path atomically:YES];NSLog(@"DIAGNOSTIC_SMOKE %@",passed?@"PASS":@"FAIL");
    });
}
@end
@interface SmokeApp : UIResponder <UIApplicationDelegate>
@end
@implementation SmokeApp
- (UISceneConfiguration *)application:(UIApplication *)app configurationForConnectingSceneSession:(UISceneSession *)session options:(UISceneConnectionOptions *)options {
    UISceneConfiguration *configuration=[[UISceneConfiguration alloc]initWithName:@"Default" sessionRole:session.role];configuration.delegateClass=SmokeScene.class;return configuration;
}
@end
int main(int argc,char **argv){@autoreleasepool{return UIApplicationMain(argc,argv,nil,NSStringFromClass(SmokeApp.class));}}
