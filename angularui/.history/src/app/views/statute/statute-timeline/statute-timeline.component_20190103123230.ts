import { Component, OnInit, AfterViewInit , OnDestroy, ElementRef, ViewChild } from '@angular/core';
import { VisTimelineService, VisTimelineItems , VisTimelineItem } from 'ngx-vis';
import { MatSnackBar  } from '@angular/material';

import { ActivatedRoute } from '@angular/router';
import { StatuteService } from '../statute.service';
import { AppLoaderService } from '@app/shared/services/app-loader/app-loader.service';

import { StatuteHistoryItem } from '@app/shared/models/legal.models';
import { Subscription } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { ChangeDetectorRef } from '@angular/core';

@Component({
  selector: 'app-statute-timeline',
  templateUrl: './statute-timeline.component.html',
  styleUrls: ['./statute-timeline.component.scss']
})
export class StatuteTimelineComponent implements OnInit, OnDestroy {

  @ViewChild('visElement') 
  timelineContainer: ElementRef;
  
  public visTimeline: string = 'visTimeline';
  public visTimelineItems: VisTimelineItems;
  public statuteID;
  public statuteHistory: StatuteHistoryItem[];
  public getLawSub: Subscription;

  constructor(
    private visTimelineService: VisTimelineService,
    private route: ActivatedRoute,
    private statuteService: StatuteService,
    private snack: MatSnackBar,
    private loader: AppLoaderService,
    private ref: ChangeDetectorRef
    ) { }
  public timelineInitialized(): void {

    // console.log('timeline initialized');
    // now we can use the service to register on events
    this.visTimelineService.on(this.visTimeline, 'click');

    // open your console/dev tools to see the click params

    this.visTimelineService.click

        .subscribe((eventData: any[]) => {

            if (eventData[0] === this.visTimeline) {

                console.log(eventData[1]);

            }

        });
       
        
        this.visTimelineService.setItems(this.visTimeline,this.visTimelineItems);
        setTimeout(() => {
          this.visTimelineService.redraw(this.visTimeline);
          this.visTimelineService.fit(this.visTimeline);
          console.log('redraw');
        });
        this.ref.detach();
        
        this.ref.detectChanges();
        this.ref.reattach();
        this.ref.markForCheck();
       

}



public addItem(): void {

    const newLength = this.visTimelineItems.getLength() + 1;

    this.visTimelineItems.add(

        {id: newLength, content: 'Σήμερα ' + newLength, start: Date.now() },

    );

    this.visTimelineService.focusOnIds(this.visTimeline, [1, newLength]);

}

  ngOnInit(): void {
    this.visTimelineItems  = new VisTimelineItems([
      {id: 1, content: 'exam 1', start: '2018-04-20', title: "total images 6"},
      {id: 2, content: 'exam 2', start: '2018-04-14', title: "total images 6"},
      {id: 3, content: 'exam 3', start: '2018-04-18'},
      {id: 4, content: 'exam 4', start: '2018-04-16', end: '2013-04-19'},
      {id: 5, content: 'exam 5', start: '2018-04-25'},
      {id: 6, content: 'exam 6', start: '2018-04-27'},

      {id: 7, content: 'exam 1', start: '2018-05-01'},
      {id: 8, content: 'exam 2', start: '2018-05-05'},
      {id: 9, content: 'exam 3', start: '2018-05-12'},
      {id: 10, content: 'exam 4', start: '2018-05-15', end: '2013-04-19'},
      {id: 11, content: 'exam 5', start: '2018-05-25'},
      {id: 12, content: 'exam 6', start: '2018-05-27'},
      
    ]);
    this.statuteID = this.route.parent.snapshot.params['id'];
    this.getStatuteHistory();


  //this.visTimelineService.focusOnIds(this.visTimeline, [1, 6]);

};

ngAfterViewInit() {     

  this.ref.detach();
  
  this.ref.detectChanges();
  this.ref.reattach();
  this.ref.markForCheck();

  
 
}

getStatuteHistory() {

    setTimeout(() => {
      this.loader.open();
    });


    this.getLawSub =  this.statuteService.getStatuteHistory(this.statuteID)
    .pipe(
      finalize(() =>  {
      this.loader.close();
    })
    )
    .subscribe(data => {
      this.statuteHistory = data;
/*       this.visTimelineItems = new VisTimelineItems(
          data.map(item => <VisTimelineItem>
          {
            id:item.identifier+item.amendee,
            content:item.amendee,
            start: item.amendee_date
          }) //end map
          
        ); */
     
        console.log('got data');
   
    },
    err => {
    this.snack.open("Πρόβλημα κατά την ανάκτηση δεδομένων!", 'OK', { duration: 4000 });
    }  
    ); //end subscribe
}


public ngOnDestroy(): void {

  this.visTimelineService.off(this.visTimeline, 'click');

}

}
