import { Component, OnInit, OnDestroy , ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { egretAnimations } from '@app/shared/animations/egret-animations';
import { AppLoaderService } from '@app/shared/services/app-loader/app-loader.service';
import { StatuteService } from '../statute.service';

import { MatSnackBar  } from '@angular/material';

import { Subscription  } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { Topic } from '@app/shared/models/legal.models';


@Component({
  selector: 'app-statute-topics',
  templateUrl: './statute-topics.component.html',
  styleUrls: ['./statute-topics.component.scss'],
  animations: egretAnimations,
  providers: [StatuteService]
})
export class StatuteTopicsComponent implements OnInit, OnDestroy {
  public statuteID: string;
  public topic: Topic = { _id:0 , keywords:[] , statutes:[] };
  public getLawSub: Subscription;

  constructor(
    private statuteService: StatuteService,
    private route: ActivatedRoute,
    private snack: MatSnackBar,
    private loader: AppLoaderService,
  ) { }

  ngOnInit() {
    this.statuteID = this.route.parent.snapshot.params['id'];
    this.getStatuteTopics();
  }

  ngOnDestroy() {
    if (this.getLawSub) {
      this.getLawSub.unsubscribe();
    }
   
  }

  getStatuteTopics() {
  
  setTimeout(() => {
    this.loader.open();
  });


  this.getLawSub =  this.statuteService.getStatuteTopics(this.statuteID)
  .pipe(
    finalize(() =>  {
    this.loader.close();
  })
  )
  .subscribe(data => {
    this.topic = data;
  },
  err => {
  this.snack.open("Πρόβλημα κατά την ανάκτηση δεδομένων!", 'OK', { duration: 4000 });
  }  
  );
  
}

 

}
