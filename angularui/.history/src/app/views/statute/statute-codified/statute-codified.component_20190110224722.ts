import { Component, OnInit, OnDestroy , ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { egretAnimations } from '@app/shared/animations/egret-animations';
import { AppLoaderService } from '@app/shared/services/app-loader/app-loader.service';
import { StatuteService } from '../statute.service';

import { MatSnackBar  } from '@angular/material';

import { Subscription  } from 'rxjs';
import { finalize } from 'rxjs/operators';

@Component({
  selector: 'app-statute-codified',
  templateUrl: './statute-codified.component.html',
  styleUrls: ['./statute-codified.component.scss'],
  animations: egretAnimations,
  providers: [StatuteService]
})
export class StatuteCodifiedComponent implements OnInit, OnDestroy {
  public statuteID: string;
  public codified_content: string;
  public getLawSub: Subscription;


  constructor(
    private statuteService: StatuteService,
    private route: ActivatedRoute,
    private snack: MatSnackBar,
    private loader: AppLoaderService,
  ) { }

  ngOnInit() {
    this.statuteID = this.route.parent.snapshot.params['id'];
    this.getCodifiedStatute();
  }

  ngOnDestroy() {
    if (this.getLawSub) {
      this.getLawSub.unsubscribe();
    }
   
  }

  getCodifiedStatute() {

  setTimeout(() => {
    this.loader.open();
  });

  this.getLawSub =  this.statuteService.getStatuteCodified(this.statuteID)
  .pipe(
    finalize(() =>  {
    this.loader.close();
  })
  )
  .subscribe(data => {
    this.codified_content = data;
  },
  err => {
  this.snack.open('Πρόβλημα κατά την ανάκτηση δεδομένων!', 'OK', { duration: 4000 });
  }
  );

}




}
