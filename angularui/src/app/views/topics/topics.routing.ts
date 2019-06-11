import { Routes } from '@angular/router';


import { TopicsComponent } from './topics.component';


export const TopicsRoutes: Routes = [
  {
    path: '',
    component: TopicsComponent,
    data: { title: 'Θεματικές', breadcrumb: 'Θεματικές' },
  }
];
