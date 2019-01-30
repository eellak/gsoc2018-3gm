import { Component, OnInit, AfterViewInit , OnDestroy, ElementRef, ViewChild, ApplicationRef } from '@angular/core';
import { VisTimelineService, VisTimelineItems , VisTimelineItem, VisTimeline, VisTimelineOptions } from 'ngx-vis';
import { MatSnackBar  } from '@angular/material';

import { ActivatedRoute } from '@angular/router';
import { StatuteService } from '../statute.service';
import { AppLoaderService } from '@app/shared/services/app-loader/app-loader.service';

import { StatuteHistoryItem } from '@app/shared/models/legal.models';
import { Subscription } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { ChangeDetectorRef } from '@angular/core';
import { Url2StatutePipe } from '@app/shared/pipes/url2statute.pipe';

@Component({
  selector: 'app-statute-timeline',
  templateUrl: './statute-timeline.component.html',
  styleUrls: ['./statute-timeline.component.scss']
})
export class StatuteTimelineComponent implements OnInit, OnDestroy {

 
  
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
    private ref: ChangeDetectorRef,
    private ap: ApplicationRef
    ) { }
  public timelineInitialized(): void {

    // console.log('timeline initialized');
    // now we can use the service to register on events
    this.visTimelineService.on(this.visTimeline, 'click');
    this.visTimelineService.on(this.visTimeline, 'rangechanged');

    // open your console/dev tools to see the click params

    this.visTimelineService.click

        .subscribe((eventData: any[]) => {

            if (eventData[0] === this.visTimeline) {

              const eventdata = eventData[1];
              if (eventdata && eventdata['what']==='item') {
                const selected_item = eventdata['item'];
                console.log(selected_item);
                const history_item = this.statuteHistory.find(item => item.amendee===selected_item);
                if (history_item.summary && history_item.summary.length>10)
                  this.snack.open(history_item.summary,'OK' , { duration: 6000 });
                console.log(history_item.summary);
              }

            }

        });

        this.visTimelineService.rangechanged

        .subscribe((eventData: any[]) => {

            if (eventData[0] === this.visTimeline) {
                const eventdata = eventData[1];
                if (eventdata['what']==='item') {
                  const item = eventdata['item'];
                  console.log(item);
                }
            }

        });
        console.log('timelineInitialized');

        setTimeout(() => {
         const element: HTMLElement = document.getElementById('addbtn') as HTMLElement;
         element.click();

        //  this.visTimelineService.setItems(this.visTimeline,this.visTimelineItems);
        //   this.visTimelineService.redraw(this.visTimeline);
        //   this.visTimelineService.fit(this.visTimeline);

        //   this.visTimelineService.focusOnIds(this.visTimeline, this.visTimelineItems.getIds());
          this.ap.tick();

      }, 1000);
/*         this.visTimelineService.setItems(this.visTimeline,this.visTimelineItems);
        setTimeout(() => {
          this.visTimelineService.redraw(this.visTimeline);
          this.visTimelineService.fit(this.visTimeline);
          console.log('redraw');
          this.ref.markForCheck();
        
        });
        this.ref.detach();
        let element : HTMLElement = document.getElementById('addbtn') as HTMLElement;
        element.click();
        
        this.ref.detectChanges();
        this.ref.reattach();
        this.ref.markForCheck(); */


}



public addItem(): void {

    const newLength = this.visTimelineItems.getLength() + 1;

    this.visTimelineItems.add(

        {id: newLength, content: 'Σήμερα ' + newLength, start: Date.now() },

    );

    //this.visTimelineService.focusOnIds(this.visTimeline, [1, newLength]);
    //this.visTimelineService.focusOnIds(this.visTimeline, this.visTimelineItems.getIds(),{animation: {duration: 3000, easingFunction: 'linear'}});

}

  ngOnInit(): void {
    this.statuteID = this.route.parent.snapshot.params['id'];
   


  //this.visTimelineService.focusOnIds(this.visTimeline, [1, 6]);

};

ngAfterViewInit() {     
  this.getStatuteHistory();


  /* let tlContainer = this.timelineContainer.nativeElement;       
  this.addItem();


  this.ref.detach();
  
  this.ref.detectChanges();
  this.ref.reattach();
  this.ref.markForCheck();
 */
 
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
      this.visTimelineItems = new VisTimelineItems(
          data.map(item => <VisTimelineItem>
          {
            id:item.amendee || item.identifier,
            title:new Url2StatutePipe().transform(item.amendee),
            content:`<i class="mat-icon material-icons">description</i> <div><a href='/statute/${item.amendee}'>${new Url2StatutePipe().transform(item.amendee)}</a></div>`,
            start: item.amendee_date
          }) //end map
          
        );
        let mindate = this.visTimelineItems.min('start').start;
        let maxdate = new Date();

        console.log('got data');
        let options: VisTimelineOptions = {
          height: '300px',
          min: mindate,    // lower limit of visible range
          max: maxdate,   // upper limit of visible range
          timeAxis: {scale:'month', step:1},
          zoomMin: 1000 * 60 * 60 * 24 * 31,             // one month in milliseconds
          zoomMax: 1000 * 60 * 60 * 24 * 31 * 12     // about twelve months in milliseconds
        };
        this.visTimelineService.setOptions(this.visTimeline,options);
       
    },
    err => {
    this.snack.open("Πρόβλημα κατά την ανάκτηση δεδομένων!", 'OK', { duration: 4000 });
    }  
    ); //end subscribe
}

public fit(){
  this.visTimelineService.fit(this.visTimeline)
}
public ngOnDestroy(): void {

  this.visTimelineService.off(this.visTimeline, 'click');

}

}
