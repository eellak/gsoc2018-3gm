import { Component, OnInit, OnDestroy, AfterViewInit } from '@angular/core';
import { Router } from '@angular/router'
import { AppLoaderService } from '../../shared/services/app-loader/app-loader.service';
// import PerfectScrollbar from 'perfect-scrollbar';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html'
})
export class HomeComponent implements OnInit, OnDestroy, AfterViewInit {
  /****** Only for demo) **********/
  public versions: any[] = [
    {
      name: 'Side Navigation',
      photo: 'assets/images/screenshots/side-simple-ltr.png',
      dest: 'dashboard',
      conf: `{
        "navigationPos": "side",
        "sidebarStyle": "full",
        "dir": "ltr",
        "useBreadcrumb": true,
        "topbarFixed": false,
        "breadcrumb": "simple"
      }`
    }, {
      name: 'Top Navigation',
      photo: 'assets/images/screenshots/top-simple-ltr.png',
      dest: 'shop',
      conf: `{
        "navigationPos": "top",
        "sidebarStyle": "full",
        "dir": "ltr",
        "useBreadcrumb": true,
        "topbarFixed": false,
        "breadcrumb": "simple"
      }`
    },
    {
      name: 'RTL (Side Nav)',
      photo: 'assets/images/screenshots/side-simple-rtl.png',
      dest: 'profile/settings',
      conf: `{
        "navigationPos": "side",
        "sidebarStyle": "full",
        "dir": "rtl",
        "useBreadcrumb": true,
        "topbarFixed": false,
        "breadcrumb": "simple"
      }`
    },
    {
      name: 'RTL (Top Nav)',
      photo: 'assets/images/screenshots/top-simple-rtl.png',
      dest: 'profile/settings',
      conf: `{
        "navigationPos": "top",
        "sidebarStyle": "full",
        "dir": "rtl",
        "useBreadcrumb": true,
        "topbarFixed": false,
        "breadcrumb": "simple"
      }`
    },
    {
      name: 'Dark Purple',
      photo: 'assets/images/screenshots/dark-purple-title.png',
      dest: 'dashboard',
      conf: `{
        "navigationPos": "side",
        "sidebarStyle": "full",
        "dir": "ltr",
        "useBreadcrumb": true,
        "topbarFixed": true,
        "breadcrumb": "simple"
      }`,
      theme: `{
        "name": "egret-dark-purple"
      }`
    },
    {
      name: 'Dark Pink',
      photo: 'assets/images/screenshots/dark-pink-title.png',
      dest: 'dashboard',
      conf: `{
        "navigationPos": "side",
        "sidebarStyle": "full",
        "dir": "ltr",
        "useBreadcrumb": true,
        "topbarFixed": true,
        "breadcrumb": "simple"
      }`,
      theme: `{
        "name": "egret-dark-pink"
      }`
    },
    {
      name: 'Light Blue',
      photo: 'assets/images/screenshots/light-blue-title.png',
      dest: 'dashboard',
      conf: `{
        "navigationPos": "side",
        "sidebarStyle": "full",
        "dir": "ltr",
        "useBreadcrumb": true,
        "topbarFixed": true,
        "breadcrumb": "simple"
      }`,
      theme: `{
        "name": "egret-blue"
      }`
    }
  ]

  // private homePS: PerfectScrollbar;
  constructor(
    private router: Router,
    private loader: AppLoaderService
  ) { }

  ngOnInit() {
  }

  ngOnDestroy() {
    // if (this.homePS) this.homePS.destroy();
    this.loader.close();
  }
  ngAfterViewInit() {
    // setTimeout(() => {
    //   this.homePS = new PerfectScrollbar('.scrollable')
    // });
  }

  /****** Remove this (Only for demo) **********/
  goToDashboard(v) {
    let origin = window.location.origin;
    if(v.theme) {
      return window.location.href = `${origin}/${v.dest}/?layout=${v.conf}&theme=${v.theme}`;
    }
    window.location.href = `${origin}/${v.dest}/?layout=${v.conf}`;
  }
  goToMainDash() {
    this.loader.open();
    this.router.navigateByUrl('/dashboard')
  }
}
