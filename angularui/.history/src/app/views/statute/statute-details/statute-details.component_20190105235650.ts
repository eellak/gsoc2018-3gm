import { Component, OnInit, OnDestroy , ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { egretAnimations } from '@app/shared/animations/egret-animations';
import { AppLoaderService } from '@app/shared/services/app-loader/app-loader.service';
import { StatuteService } from '../statute.service';

import { MatSnackBar , MatSidenav } from '@angular/material';
import { MediaChange, ObservableMedia } from '@angular/flex-layout';

import { Statute , Article , Paragraph } from '@app/shared/models/legal.models';
import { Subscription  } from 'rxjs';
import { finalize } from 'rxjs/operators';

@Component({
  selector: 'app-statute-details',
  templateUrl: './statute-details.component.html',
  styleUrls: ['./statute-details.component.scss'],
  animations: egretAnimations,
  providers: [StatuteService]
})
export class StatuteDetailsComponent implements OnInit, OnDestroy {
  isMobile;
  screenSizeWatcher: Subscription;
  isSidenavOpen: Boolean = true;
  expandToggleFlag = false;
  @ViewChild(MatSidenav) private sideNav: MatSidenav;
  articles;

  public statuteID: string;
  public statute: Statute = { _id: '0' , name: 0, type: '', year: 0 , rank: 1 , articles: {} }  ;
  public getLawSub: Subscription;
  public getArticleSub: Subscription;


  constructor(
    private media: ObservableMedia,
    private statuteService: StatuteService,
    private route: ActivatedRoute,
    private snack: MatSnackBar,
    private loader: AppLoaderService,
  ) { }

  ngOnInit() {
    this.statuteID = this.route.parent.snapshot.params['id'];
    this.getLaw();
  }

  ngOnDestroy() {
    if (this.getLawSub) {
      this.getLawSub.unsubscribe();
    }
    if (this.getArticleSub) {
      this.getArticleSub.unsubscribe();
    }

  }

getLaw() {
  
  setTimeout(() => {
    this.loader.open();
  });


  this.getLawSub =  this.statuteService.getStatuteDetails(this.statuteID)
  .pipe(
    finalize(() =>  {
    this.loader.close();
  })
  )
  .subscribe(data => {
    this.statute = data;
  },
  err => {
  this.snack.open("Πρόβλημα κατά την ανάκτηση δεδομένων!", 'OK', { duration: 4000 });
  }  
  );
  
}

getArticle(articleID: string) {
  this.getArticleSub =  this.statuteService.getStatuteArticle(this.statuteID, articleID)
  .subscribe(article => {

    //this.statute.articles[articleID] = article ;//#{'1' : ['a', 'b']};

    // see https://blog.angular-university.io/angular-debugging/ & https://github.com/angular/angular/issues/17572
    // setTimeout(() => this.snack.open(this.statute.name, 'OK', { duration: 4000 }) );
  });
}

fetchArticle(articleID) {
  //this.getArticle(articleID);
}

articleComparator(a, b) {
  if (a.key === b.key) {
  return 0;
  }
  return Number(a.key) < (b.key) ? -1 : 1;
  }


  viewVersions() {
    this.snack.open(this.statute.titleGR, 'OK', { duration: 4000 }) ;
  }

  // UI
  expandToggleAll() {
    this.expandToggleFlag = !this.expandToggleFlag;
    //this.messages.forEach((msg) => { msg.selected = this.selectToggleFlag });
  }
  updateSidenav() {
    const self = this;
    setTimeout(() => {
      self.isSidenavOpen = !self.isMobile;
      self.sideNav.mode = self.isMobile ? 'over' : 'side';
    })
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
