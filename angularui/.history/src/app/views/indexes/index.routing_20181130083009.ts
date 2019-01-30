import { Routes } from '@angular/router';
import { IndexTableComponent } from './index-table/index-table.component';
import { StatuteDetailsComponent } from './statute-details/statute-details.component';


export const IndexRoutes: Routes = [{
  path: '',
  children: [{
    path: '',
    component: IndexTableComponent
  }, {
    path: 'statutes/:id',
    component: StatuteDetailsComponent,
    data: { title: '{{ id }}', breadcrumb: 'Νομοθέτημα' }
  }, ]
}];

