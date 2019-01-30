import { Routes } from '@angular/router';

import { StatuteComponent } from './statute.component';
import { StatuteArticlesComponent } from './statute-articles/statute-articles.component';
import { StatuteCodifiedComponent } from './statute-codified/statute-codified.component';
import { StatuteHistoryComponent } from './statute-history/statute-history.component';
import { StatuteDiffComponent } from './statute-diff/statute-diff.component';
import { StatuteTimelineComponent } from './statute-timeline/statute-timeline.component';
import { StatuteReferencesComponent } from './statute-references/statute-references.component';

export const StatuteRoutes: Routes = [
  {
    path: ':id',
    component: StatuteComponent,
    data: { title: '{{ id }}', breadcrumb: '{{ id }}' },
    children: [  {
      path: '',
      redirectTo: 'codified',
      pathMatch: 'full'
     },
      {
      path: 'articles',
      component: StatuteArticlesComponent,
      data: { title: '{{ id }}', breadcrumb: 'Αρχική έκδοση' }
    },
    {
      path: 'codified',
      component: StatuteCodifiedComponent,
      data: { title: '{{ id }}', breadcrumb: 'Κωδικοποιημένη έκδοση' }
    },
    {
      path: 'history',
      component: StatuteHistoryComponent,
      data: { title: 'Ιστορία', breadcrumb: 'Ιστορία' }
    },
    {
      path: 'timeline',
      component: StatuteTimelineComponent,
      data: { title: 'Timeline', breadcrumb: 'TIMELINE' }
    },
    {
      path: 'links',
      component: StatuteReferencesComponent,
      data: { title: 'Links', breadcrumb: 'RELATIONSHIPS' }
    }
  ]
  },
  {
    path: 'diff/:id/:amendeeId',
    component: StatuteDiffComponent,
    data: { title: '{{ id }}', breadcrumb: 'DIFF' }
  }
];
