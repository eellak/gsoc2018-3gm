import { Component, OnInit, OnDestroy } from '@angular/core';
import { VisTimelineService, VisTimelineItems } from 'ngx-vis';

@Component({
  selector: 'app-statute-blank',
  templateUrl: './statute-blank.component.html',
  styleUrls: ['./statute-blank.component.css']
})
export class StatuteBlankComponent implements OnInit, OnDestroy {

  public visTimeline: string = 'timelineId1';
  public visTimelineItems: VisTimelineItems;

  constructor(private visTimelineService: VisTimelineService) { }
  public timelineInitialized(): void {

    console.log('timeline initialized');
    // now we can use the service to register on events
    this.visTimelineService.on(this.visTimeline, 'click');

    // open your console/dev tools to see the click params

    this.visTimelineService.click

        .subscribe((eventData: any[]) => {

            if (eventData[0] === this.visTimeline) {

                console.log(eventData[1]);

            }

        });

}



public addItem(): void {

    const newLength = this.visTimelineItems.getLength() + 1;

    this.visTimelineItems.add(

        {id: newLength, content: 'item ' + newLength, start: Date.now() },

    );

    this.visTimelineService.focusOnIds(this.visTimeline, [1, newLength]);

}

  ngOnInit(): void {
    this.visTimelineItems = new VisTimelineItems([

      {id: 1, content: 'item 1', start: '2016-04-20'},

      {id: 2, content: 'item 2', start: '2017-04-14'},

      {id: 3, content: 'item 3', start: '2012-04-18'},

      {id: 4, content: 'item 4', start: '2011-04-16'},

      {id: 5, content: 'item 5', start: '2010-04-25'},

      {id: 6, content: 'item 6', start: '2010-04-20', type: 'point'},

  ]);

}



public ngOnDestroy(): void {

  this.visTimelineService.off(this.visTimeline, 'click');

}

}
