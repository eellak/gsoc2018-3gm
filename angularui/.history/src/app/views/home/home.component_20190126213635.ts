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
    },
    {
      name: 'Top Navigation',
      photo: 'assets/images/screenshots/top-simple-ltr.png',
      dest: 'shop',
    },
    {
      name: 'RTL (Side Nav)',
      photo: 'assets/images/screenshots/side-simple-rtl.png',
      dest: 'profile/settings',
    },
    {
      name: 'RTL (Top Nav)',
      photo: 'assets/images/screenshots/top-simple-rtl.png',
      dest: 'profile/settings',
    },
    {
      name: 'Dark Purple',
      photo: 'assets/images/screenshots/dark-purple-title.png',
      dest: 'dashboard',
      theme: `{
        "name": "egret-dark-purple"
      }`
    },
    {
      name: 'Dark Pink',
      photo: 'assets/images/screenshots/dark-pink-title.png',
      dest: 'dashboard',
      theme: `{
        "name": "egret-dark-pink"
      }`
    },
    {
      name: 'Light Blue',
      photo: 'assets/images/screenshots/light-blue-title.png',
      dest: 'dashboard',
      theme: `{
        "name": "egret-blue"
      }`
    }
  ];

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

  goToDashboard(v) {
    this.loader.open();
    this.router.navigateByUrl(v.dest);
  }

  goToMainDash() {
    this.loader.open();
    this.router.navigateByUrl('/dashboard');
  }
}
