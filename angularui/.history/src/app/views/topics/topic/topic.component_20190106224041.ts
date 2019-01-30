import { Component, OnInit, OnDestroy , ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { egretAnimations } from '@app/shared/animations/egret-animations';
import { AppLoaderService } from '@app/shared/services/app-loader/app-loader.service';
import { TopicsService } from './topics.service';

import { MatSnackBar  } from '@angular/material';

import { Subscription  } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { Topic } from '@app/shared/models/legal.models';

import {  isNilOrEmpty } from '@app/shared/helpers/utils';

@Component({
  selector: 'app-topics',
  templateUrl: './topics.component.html',
  styleUrls: ['./topics.component.scss'],
  animations: egretAnimations,
  providers: [TopicsService]
})
export class TopicsComponent implements OnInit, OnDestroy {
  public statuteID: string;
  public topics: Topic[] = [{ _id:0 , keywords:[] , statutes:[] }];
  public getLawSub: Subscription;

  constructor(
    private topicsService: TopicsService,
    private router:Router,
    private route: ActivatedRoute,
    private snack: MatSnackBar,
    private loader: AppLoaderService,
  ) { }

  ngOnInit() {
     this.getTopics();
  }

  ngOnDestroy() {
    if (this.getLawSub) {
      this.getLawSub.unsubscribe();
    }
   
  }

  getTopics() {
  
  setTimeout(() => {
    this.loader.open();
  });


  this.getLawSub =  this.topicsService.getTopics()
  .pipe(
    finalize(() =>  {
    this.loader.close();
  })
  )
  .subscribe(data => {
    this.topics = data;
  },
  err => {
  this.snack.open("Πρόβλημα κατά την ανάκτηση δεδομένων!", 'OK', { duration: 4000 });
  }  
  );
  
}

isSelected(item:string):boolean{
    return (!isNilOrEmpty(item) && item.startsWith('ν'))
}

}
