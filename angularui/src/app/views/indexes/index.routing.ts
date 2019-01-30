import { Routes } from '@angular/router';
import { IndexTableComponent } from './index-table/index-table.component';



export const IndexRoutes: Routes = [{
  path: '',
  children: [{
    path: '',
    component: IndexTableComponent
  } ]
}];

