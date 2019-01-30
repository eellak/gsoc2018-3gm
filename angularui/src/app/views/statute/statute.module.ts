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

import { StatuteComponent } from './statute.component';
import { StatuteArticlesComponent } from './statute-articles/statute-articles.component';
import { StatuteCodifiedComponent } from './statute-codified/statute-codified.component';
import { StatuteHistoryComponent } from './statute-history/statute-history.component';
import { StatuteDiffComponent } from './statute-diff/statute-diff.component';
import { StatuteTimelineComponent } from './statute-timeline/statute-timeline.component';
import { StatuteTopicsComponent } from './statute-topics/statute-topics.component';
import { StatuteRoutes } from './statute.routing';
import { StatuteReferencesComponent } from './statute-references/statute-references.component';


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
    RouterModule.forChild(StatuteRoutes)
  ],
  declarations: [StatuteComponent, StatuteArticlesComponent, StatuteCodifiedComponent,  StatuteHistoryComponent, StatuteDiffComponent ,  StatuteTimelineComponent, StatuteTopicsComponent , StatuteReferencesComponent]
})
export class StatuteModule { }
