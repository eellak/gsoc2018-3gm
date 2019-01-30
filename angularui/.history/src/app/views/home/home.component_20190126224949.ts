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
      name: 'Main Dashboard',
      photo: 'assets/images/screenshots/dashboard.png',
      dest: 'dashboard',
    },
    {
      name: 'Articles',
      photo: 'assets/images/screenshots/articles.png',
      dest: 'statute/l_4009_2011/articles',
    },
    {
      name: 'Relationships',
      photo: 'assets/images/screenshots/relationships.png',
      dest: 'profile/settings',
    },
    {
      name: 'Compare',
      photo: 'assets/images/screenshots/compare.png',
      dest: 'profile/settings',
    },
    {
      name: 'Search (light)',
      photo: 'assets/images/screenshots/search_light.png',
      dest: 'dashboard',
      theme: `{
        "name": "egret-dark-purple"
      }`
    },
    {
      name: 'Statute',
      photo: 'assets/images/screenshots/statute.png',
      dest: 'dashboard',
      theme: `{
        "name": "egret-dark-pink"
      }`
    },
    {
      name: 'Timeline (Light Blue)',
      photo: 'assets/images/screenshots/timeline_light.png',
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
