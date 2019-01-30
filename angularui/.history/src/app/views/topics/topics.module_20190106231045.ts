import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import {
  MatToolbarModule,
  MatSidenavModule,
  MatListModule,
  MatIconModule,
  MatButtonModule,
  MatButtonToggleModule,
  MatCardModule,
  MatMenuModule,
  MatSlideToggleModule,
  MatGridListModule,
  MatChipsModule,
  MatCheckboxModule,
  MatRadioModule,
  MatTabsModule,
  MatInputModule,
  MatProgressBarModule,
  MatExpansionModule,
  MatTooltipModule,
  MatBadgeModule,
 } from '@angular/material';
import { FlexLayoutModule } from '@angular/flex-layout';
import { NgxDatatableModule } from '@swimlane/ngx-datatable';
import { ChartsModule } from 'ng2-charts/ng2-charts';
import { MglTimelineModule } from 'angular-mgl-timeline';
import { VisModule } from 'ngx-vis';
import { SharedModule } from '../../shared/shared.module';


import { TopicsComponent } from './topics.component';
import { TopicsRoutes } from './topics.routing';


@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    MatToolbarModule,
    MatSidenavModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatButtonToggleModule,
    MatCardModule,
    MatMenuModule,
    MatSlideToggleModule,
    MatGridListModule,
    MatChipsModule,
    MatCheckboxModule,
    MatRadioModule,
    MatTabsModule,
    MatInputModule,
    MatProgressBarModule,
    MatExpansionModule,
    MatTooltipModule,
    MatBadgeModule,
    FlexLayoutModule,
    NgxDatatableModule,
    ChartsModule,
    MglTimelineModule,
    VisModule,
    SharedModule,
    RouterModule.forChild(TopicsRoutes)
  ],
  declarations: [  TopicsComponent ] 
})

export class TopicsModule { }
