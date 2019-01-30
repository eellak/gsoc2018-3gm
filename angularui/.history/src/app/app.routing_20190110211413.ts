import { Routes } from '@angular/router';
import { AdminLayoutComponent } from './shared/components/layouts/admin-layout/admin-layout.component';
import { AuthLayoutComponent } from './shared/components/layouts/auth-layout/auth-layout.component';
import { AuthGuard } from './shared/services/auth/auth.guard';

export const rootRouterConfig: Routes = [
  {
    path: '',
    redirectTo: 'home',
    pathMatch: 'full'
  },
  {
    path: 'home',
    loadChildren: './views/home/home.module#HomeModule',
    data: { title: 'Choose A Demo' }
  },
  {
    path: '',
    component: AuthLayoutComponent,
    children: [
      {
        path: 'sessions',
        loadChildren: './views/sessions/sessions.module#SessionsModule',
        data: { title: 'Session'}
      }
    ]
  },
  {
    path: '',
    component: AdminLayoutComponent,
    canActivate: [AuthGuard],
    children: [
      {
        path: 'dashboard',
        loadChildren: './views/dashboard/dashboard.module#DashboardModule',
        data: { title: 'Πύλη Κωδικοποίησης', breadcrumb: 'DASHBOARD'}
      },
      {
        path: 'others',
        loadChildren: './views/others/others.module#OthersModule',
        data: { title: 'Others', breadcrumb: 'OTHERS'}
      },
      {
        path: 'legalindex',
        loadChildren: './views/indexes/index.module#IndexModule',
        data: { title: 'Ευρετήριο', breadcrumb: 'Index'}
      },
      {
        path: 'statute',
        loadChildren: './views/statute/statute.module#StatuteModule',
        data: { title: 'Νομοθέτημα', breadcrumb: 'Νομοθέτημα'}
      },
      {
        path: 'topics',
        loadChildren: './views/topics/topics.module#TopicsModule',
        data: { title: 'Θεματικές', breadcrumb: 'Θεματικές'}
      },
    ]
  },
  {
    path: '**',
    redirectTo: 'sessions/404'
  }
];

