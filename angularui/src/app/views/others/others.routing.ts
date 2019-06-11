import { Routes } from '@angular/router';
import { AppBlankComponent } from './app-blank/app-blank.component';
import { AboutComponent } from './about/about.component';

export const OthersRoutes: Routes = [
  {
    path: '',
    children: [ {
      path: 'blank',
      component: AppBlankComponent,
      data: { title: 'Blank', breadcrumb: 'BLANK' }
    }, {
      path: 'about',
      component: AboutComponent,
      data: { title: 'Σχετικά', breadcrumb: 'ABOUT' }
    }, ]
  }
];
