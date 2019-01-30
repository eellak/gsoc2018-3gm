import { Component, OnInit, AfterViewInit, ViewChild, HostListener } from '@angular/core';
import {
  Router,
  NavigationEnd,
  RouteConfigLoadStart,
  RouteConfigLoadEnd,
  ResolveStart,
  ResolveEnd
} from '@angular/router';
import { Subscription } from 'rxjs';
import { MatSidenav } from '@angular/material';
import { MediaChange, ObservableMedia } from '@angular/flex-layout';
import { ThemeService } from '../../../services/theme.service';
// import PerfectScrollbar from 'perfect-scrollbar';
import { LayoutService } from '../../../services/layout.service';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-admin-layout',
  templateUrl: './admin-layout.template.html'
})
export class AdminLayoutComponent implements OnInit, AfterViewInit {
  public isModuleLoading: Boolean = false;
  private moduleLoaderSub: Subscription;
  private layoutConfSub: Subscription;
  private routerEventSub: Subscription;
  private mediaSub: Subscription;
  // private sidebarPS: PerfectScrollbar;

  // private bodyPS: PerfectScrollbar;
  // private headerFixedBodyPS: PerfectScrollbar;
  public  scrollConfig = {}
  public layoutConf: any = {};

  constructor(
    private router: Router,
    public themeService: ThemeService,
    private layout: LayoutService,
    private media: ObservableMedia
  ) {
    // Close sidenav after route change in mobile
    this.routerEventSub = router.events.pipe(filter(event => event instanceof NavigationEnd))
    .subscribe((routeChange: NavigationEnd) => {
      this.layout.adjustLayout({ route: routeChange.url });
    });

  }
  ngOnInit() {
    this.layoutConf = this.layout.layoutConf;
    // this.layout.adjustLayout();
    // console.log(this.layoutConf)

    // FOR MODULE LOADER FLAG
    this.moduleLoaderSub = this.router.events.subscribe(event => {
      if(event instanceof RouteConfigLoadStart || event instanceof ResolveStart) {
        this.isModuleLoading = true;
      }
      if(event instanceof RouteConfigLoadEnd || event instanceof ResolveEnd) {
        this.isModuleLoading = false;
      }
    });
  }
  @HostListener('window:resize', ['$event'])
  onResize(event) {
    this.layout.adjustLayout(event);
  }
  
  ngAfterViewInit() {
    // this.layoutConfSub = this.layout.layoutConf$.subscribe(change => {
    //   // this.initBodyPS(change)
    // })
  }
  
  // initBodyPS(layoutConf:any = {}) {
  //   if(layoutConf.navigationPos === 'side' && layoutConf.topbarFixed) {
  //     if (this.bodyPS) this.bodyPS.destroy();
  //     if (this.headerFixedBodyPS) this.headerFixedBodyPS.destroy();
  //     this.headerFixedBodyPS = new PerfectScrollbar('.rightside-content-hold', {
  //       suppressScrollX: true
  //     });
  //     this.scrollToTop('.rightside-content-hold');
  //   } else {
  //     if (this.bodyPS) this.bodyPS.destroy();
  //     if (this.headerFixedBodyPS) this.headerFixedBodyPS.destroy();
  //     this.bodyPS = new PerfectScrollbar('.main-content-wrap', {
  //       suppressScrollX: true
  //     });
  //     this.scrollToTop('.main-content-wrap');
  //   }
  // }
  scrollToTop(selector: string) {
    if(document) {
      let element = <HTMLElement>document.querySelector(selector);
      element.scrollTop = 0;
    }
  }
  ngOnDestroy() {
    if(this.moduleLoaderSub) {
      this.moduleLoaderSub.unsubscribe()
    }
    if(this.layoutConfSub) {
      this.layoutConfSub.unsubscribe()
    }
    if(this.routerEventSub) {
      this.routerEventSub.unsubscribe()
    }
  }
  closeSidebar() {
    this.layout.publishLayoutChange({
      sidebarStyle: 'closed'
    });
  }
}
