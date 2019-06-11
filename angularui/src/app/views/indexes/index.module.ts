import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import {
  MatInputModule,
  MatIconModule,
  MatCardModule,
  MatMenuModule,
  MatButtonModule,
  MatButtonToggleModule,
  MatChipsModule,
  MatListModule,
  MatGridListModule,
  MatToolbarModule,
  MatSidenavModule,
  MatSelectModule,
  MatRadioModule,
  MatTooltipModule,
  MatDialogModule,
  MatSnackBarModule,
  MatSlideToggleModule,
  MatCheckboxModule,
  MatExpansionModule,
  MatSliderModule,
  MatBadgeModule,
 } from '@angular/material';
import { FlexLayoutModule } from '@angular/flex-layout';
import { StarRatingModule } from 'angular-star-rating';
import { NgxDatatableModule } from '@swimlane/ngx-datatable';
import { SharedModule } from '../../shared/shared.module';
import { IndexTableComponent } from './index-table/index-table.component';


import { IndexRoutes } from './index.routing';
import { IndexService } from './index.service';
import { IndexTablePopupComponent } from './index-table/index-table-popup/index-table-popup.component';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    FlexLayoutModule,
    StarRatingModule,
    NgxDatatableModule,
    MatInputModule,
    MatIconModule,
    MatCardModule,
    MatMenuModule,
    MatButtonModule,
    MatButtonToggleModule,
    MatChipsModule,
    MatListModule,
    MatGridListModule,
    MatToolbarModule,
    MatSidenavModule,
    MatSelectModule,
    MatTooltipModule,
    MatDialogModule,
    MatSnackBarModule,
    MatSliderModule,
    MatSlideToggleModule,
    MatRadioModule,
    MatCheckboxModule,
    MatExpansionModule,
    MatBadgeModule,
    SharedModule,
    RouterModule.forChild(IndexRoutes)
  ],
  declarations: [IndexTableComponent, IndexTablePopupComponent  ],
  providers: [IndexService],
  entryComponents: [IndexTablePopupComponent]
})
export class IndexModule { }
