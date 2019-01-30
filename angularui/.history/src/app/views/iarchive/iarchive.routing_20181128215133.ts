import { Routes } from '@angular/router';

import { IarchiveComponent } from './iarchive.component';
import { IarchiveOverviewComponent } from './iarchive-overview/iarchive-overview.component';
import { IarchiveTableComponent } from './iarchive-table/iarchive-table.component';
import { IarchiveBlankComponent } from './iarchive-blank/iarchive-blank.component';

export const IarchiveRoutes: Routes = [
  {
    path: '',
    component: IarchiveComponent,
    children: [
      {
       path: '',
       redirectTo: 'overview',
       pathMatch: 'full'
      },
      {
      path: 'overview',
      component: IarchiveOverviewComponent,
      data: { title: 'Overview', breadcrumb: 'OVERVIEW' }
    },
    {
      path: 'table',
      component: IarchiveTableComponent,
      data: { title: 'List', breadcrumb: 'LIST' }
    },
    {
      path: 'about',
      component: IarchiveBlankComponent,
      data: { title: 'About', breadcrumb: 'ABOUT' }
    }]
  }
];