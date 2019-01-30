import { Component, OnInit, OnDestroy } from '@angular/core';
import { VisTimelineService, VisTimelineItems , VisTimelineItem } from 'ngx-vis';
import { ActivatedRoute } from '@angular/router';
import { StatuteService } from '../statute.service';
import { StatuteHistoryItem } from '@app/shared/models/legal.models';
import { Subscription } from 'rxjs';

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


        this.visTimelineService.focusOnIds(this.visTimeline, [1, 6]);

}



public addItem(): void {

    const newLength = this.visTimelineItems.getLength() + 1;

    this.visTimelineItems.add(

        {id: newLength, content: 'Σήμερα ' + newLength, start: Date.now() },

    );

    this.visTimelineService.focusOnIds(this.visTimeline, [1, newLength]);

}

  ngOnInit(): void {
    this.statuteID = this.route.parent.snapshot.params['id'];
    this.getStatuteHistory();

    this.visTimelineItems = new VisTimelineItems([

      {id: 1, content: 'ν. 4009/2011', start: '2011-04-20'},

      {id: 2, content: 'ν. 4076/2012', start: '2012-04-14'},

      {id: 3, content: 'ν. 4115/2013', start: '2012-01-18'},

      {id: 4, content: 'ν. 4186/2013', start: '2013-04-16'},

      {id: 5, content: 'ν. 4264/2014', start: '2014-02-25'},

      {id: 6, content: 'ν. 4301/2014', start: '2014-04-20', type: 'point' , className: 'red'},

  ]);




  //this.visTimelineService.focusOnIds(this.visTimeline, [1, 6]);

};

getStatuteHistory() {
  this.getLawSub =  this.statuteService.getStatuteHistory(this.statuteID)
  .subscribe(data => {
    this.statuteHistory = data;
    this.visTimelineItems = new VisTimelineItems(
        data.map(item => <VisTimelineItem>
        {
          id:item.identifier+item.amendee,
          content:item.amendee,
          start: item.amendee_date
        }) //end map
      );
  }); //end subscribe
}


public ngOnDestroy(): void {

  this.visTimelineService.off(this.visTimeline, 'click');

}

}
