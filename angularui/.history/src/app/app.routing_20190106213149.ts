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
        data: { title: 'Dashboard', breadcrumb: 'DASHBOARD'}
      },
      {
        path: 'material',
        loadChildren: './views/material/app-material.module#AppMaterialModule',
        data: { title: 'Material', breadcrumb: 'MATERIAL'}
      },
      {
        path: 'dialogs',
        loadChildren: './views/app-dialogs/app-dialogs.module#AppDialogsModule',
        data: { title: 'Dialogs', breadcrumb: 'DIALOGS'}
      },
      {
        path: 'profile',
        loadChildren: './views/profile/profile.module#ProfileModule',
        data: { title: 'Profile', breadcrumb: 'PROFILE'}
      },
      {
        path: 'others',
        loadChildren: './views/others/others.module#OthersModule',
        data: { title: 'Others', breadcrumb: 'OTHERS'}
      },
      {
        path: 'tables',
        loadChildren: './views/tables/tables.module#TablesModule',
        data: { title: 'Tables', breadcrumb: 'TABLES'}
      },
      {
        path: 'tour',
        loadChildren: './views/app-tour/app-tour.module#AppTourModule',
        data: { title: 'Tour', breadcrumb: 'TOUR'}
      },
      {
        path: 'forms',
        loadChildren: './views/forms/forms.module#AppFormsModule',
        data: { title: 'Forms', breadcrumb: 'FORMS'}
      },
      {
        path: 'charts',
        loadChildren: './views/charts/charts.module#AppChartsModule',
        data: { title: 'Charts', breadcrumb: 'CHARTS'}
      },
      {
        path: 'map', 
        loadChildren: './views/map/map.module#AppMapModule', 
        data: { title: 'Map', breadcrumb: 'MAP'}
      },
      {
        path: 'dragndrop', 
        loadChildren: './views/dragndrop/dragndrop.module#DragndropModule', 
        data: { title: 'Drag and Drop', breadcrumb: 'DND'}
      },
      {
        path: 'inbox',
        loadChildren: './views/app-inbox/app-inbox.module#AppInboxModule', 
        data: { title: 'Inbox', breadcrumb: 'INBOX'}
      },
      {
        path: 'calendar',
        loadChildren: './views/app-calendar/app-calendar.module#AppCalendarModule',
        data: { title: 'Calendar', breadcrumb: 'CALENDAR'}
      },
      {
        path: 'chat',
        loadChildren: './views/app-chats/app-chats.module#AppChatsModule',
        data: { title: 'Chat', breadcrumb: 'CHAT'}
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
      {
        path: 'shop',
        loadChildren: './views/shop/shop.module#ShopModule',
        data: { title: 'Shop', breadcrumb: 'SHOP'}
      },
      {
        path: 'icons',
        loadChildren: './views/mat-icons/mat-icons.module#MatIconsModule',
        data: { title: 'Icons', breadcrumb: 'MATICONS'}
      }
    ]
  },
  {
    path: '**',
    redirectTo: 'sessions/404'
  }
];

