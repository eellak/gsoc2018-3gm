import { Component, OnInit, OnDestroy , ViewChild } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { egretAnimations } from '@app/shared/animations/egret-animations';
import { StatuteService } from '../statute.service';

import { MatSnackBar , MatSidenav, MatDialog } from '@angular/material';
import { MediaChange, ObservableMedia } from '@angular/flex-layout';

import { Statute ,  StatuteHistoryItem , Article , Paragraph } from '@app/shared/models/legal.models';
import { Subscription , Observable } from 'rxjs';

@Component({
  selector: 'app-statute-history',
  templateUrl: './statute-history.component.html',
  styleUrls: ['./statute-history.component.scss'],
  animations: egretAnimations,
  providers: [StatuteService]
})
export class StatuteHistoryComponent implements OnInit, OnDestroy {
  isMobile;
  screenSizeWatcher: Subscription;
  isSidenavOpen: Boolean = true;
  expandToggleFlag = false;
  @ViewChild(MatSidenav) private sideNav: MatSidenav;

  public statuteID;
  public statuteHistory: StatuteHistoryItem[];
  public getLawSub: Subscription;


  constructor(
    private media: ObservableMedia,
    private statuteService: StatuteService,
    private route: ActivatedRoute,
    private snack: MatSnackBar
  ) { }

  ngOnInit() {
    this.statuteID = this.route.parent.snapshot.params['id'];
    this.getStatuteHistory();
  }

  getStatuteHistory() {
  this.getLawSub =  this.statuteService.getStatuteHistory(this.statuteID)
  .subscribe(data => {
    // ORDER_BY last_nom, first_nom
    const unique_data = data.filter((e, i) => data.findIndex(a => a.amendee === e.amendee) === i);
    const sorted_data = unique_data.sort(( a , b ) => a.amendee_date.localeCompare(b.amendee_date) ||
                                                a.amendee.localeCompare(b.amendee)  );
    this.statuteHistory = sorted_data;
  });
}


  ngOnDestroy() {
    if (this.getLawSub) {
      this.getLawSub.unsubscribe();
    }
  }

  // UI
  expandToggleAll() {
    this.expandToggleFlag = !this.expandToggleFlag;
  }
  updateSidenav() {
    const self = this;
    setTimeout(() => {
      self.isSidenavOpen = !self.isMobile;
      self.sideNav.mode = self.isMobile ? 'over' : 'side';
    });
  }
  inboxSideNavInit() {
    this.isMobile = this.media.isActive('xs') || this.media.isActive('sm');
    this.updateSidenav();
    this.screenSizeWatcher = this.media.subscribe((change: MediaChange) => {
      this.isMobile = (change.mqAlias === 'xs') || (change.mqAlias === 'sm');
      this.updateSidenav();
    });
  }


}
