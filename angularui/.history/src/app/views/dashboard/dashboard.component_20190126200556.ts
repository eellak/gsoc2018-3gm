import { Component, OnInit, TemplateRef } from '@angular/core';
import { egretAnimations } from '@app/shared/animations/egret-animations';
import { StatuteStatsResource, LegalIndexItem } from '@app/shared/models/legal.models';
import { DashboardService } from './dashboard.service';
import { IndexService } from '../indexes/index.service';

import { FormControl } from '@angular/forms';

import { startWith, map } from 'rxjs/operators';
import { MatDialog } from '@angular/material';
import { Subscription, Observable } from 'rxjs';

import { Url2StatutePipe } from '@app/shared/pipes/url2statute.pipe';
import { Router } from '@angular/router';

import * as hopscotch from 'hopscotch';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  animations: egretAnimations,
  providers: [DashboardService, IndexService]
})
export class DashboardComponent implements OnInit {
  public legalindexitems: LegalIndexItem[] ;
  public filteredOptions: Observable<LegalIndexItem[]>;
  public getApiItemSub: Subscription;
  searchCtrl: FormControl;

  displayPipe: Url2StatutePipe;

  stats: StatuteStatsResource = {
    res_laws_total: 0,
    res_links_total: 0 ,
    res_topics_total: 0 ,
    top_5_laws: [],
    iarchive_stats: null
    } ;

    activeList: LegalIndexItem[] = [];

  photos = [{
    name: 'Part 2, 1995 no. 338',
    identifier:'GreekGovernmentGazette-19950200338',
    url: 'https://ia902901.us.archive.org/BookReader/BookReaderImages.php?zip=/12/items/GreekGovernmentGazette-19950200338/19950200338_jp2.zip&file=19950200338_jp2/19950200338_0000.jp2&scale=6&rotate=0'
  }, {
    name: 'Part 1, 1996 no. 272',
    identifier:'GreekGovernmentGazette-19960100272',
    url: 'https://ia802805.us.archive.org/BookReader/BookReaderImages.php?zip=/24/items/GreekGovernmentGazette-19960100272/19960100272_jp2.zip&file=19960100272_jp2/19960100272_0000.jp2&scale=6&rotate=0'
  }, {
    name: 'Part 1, 2016 no. 204',
    identifier:'GreekGovernmentGazette-20160100204',
    url: 'https://ia902809.us.archive.org/BookReader/BookReaderImages.php?zip=/15/items/GreekGovernmentGazette-20160100204/20160100204_jp2.zip&file=20160100204_jp2/20160100204_0000.jp2&scale=6&rotate=0'
  }, {
    name: 'Part 2, 1990 no. 222',
    identifier:'GreekGovernmentGazette-19900200222',
    url: 'https://ia802805.us.archive.org/BookReader/BookReaderImages.php?zip=/16/items/GreekGovernmentGazette-19900200222/19900200222_jp2.zip&file=19900200222_jp2/19900200222_0000.jp2&scale=6&rotate=0'
  }, {
    name: 'Part 2, 1993 no. 222',
    identifier:'GreekGovernmentGazette-19930200222',
    url: 'https://ia802805.us.archive.org/BookReader/BookReaderImages.php?zip=/13/items/GreekGovernmentGazette-19930200222/19930200222_jp2.zip&file=19930200222_jp2/19930200222_0000.jp2&scale=6&rotate=0'
  }, {
    name: 'Part 2, 2004 no. 222',
    identifier:'GreekGovernmentGazette-20040200222',
    url: 'https://ia902805.us.archive.org/BookReader/BookReaderImages.php?zip=/17/items/GreekGovernmentGazette-20040200222/20040200222_jp2.zip&file=20040200222_jp2/20040200222_0000.jp2&scale=8&rotate=0'
  }];

  // users
  users = [
    {
      "name": "Marios Papachristou",
      "membership": "Core Development",
      "phone": "+1 (956) 486-2327",
      "photo": "assets/images/faces/mp.jpg",
      "address": "Athens, Greece",
      "registered": "2016-07-09",
      "linkedin" : "https://www.linkedin.com/in/papachristoumarios/"
    },
    {
      "name": "Thodoris Papadopoulos",
      "membership": "API + UI",
      "phone": "+1 (929) 406-3172",
      "photo": "assets/images/faces/tp.jpg",
      "address": "893 Garden Place, American Samoa",
      "registered": "2017-02-16",
      "linkedin" : "https://www.linkedin.com/in/thodoris/"
    }
  ];

  constructor(
    private router: Router,
    private dashboardService: DashboardService,
    private indexService:IndexService,
    private dialog: MatDialog
    ) {
    this.searchCtrl = new FormControl();
    this.displayPipe = new Url2StatutePipe();
  }

  ngOnInit() {
    this.dashboardService.getStats().subscribe((res) =>  {
      this.stats = res;
      this.stats.top_5_laws = [
        { _id:'l_4009_2011' , name:4009 , type:'l' , year:2011 },
        { _id:'pd_19_2014' , name:19 , type:'pd' , year:2014 },
        { _id:'l_4547_2018' , name:4547 , type:'l' , year:2018 },
        { _id:'l_3978_2011' , name:3978 , type:'l' , year:2011 },
        { _id:'l_4173_2013' , name:4173 , type:'l' , year:2013 },

      ];
      this.activeList = this.stats.top_5_laws;
      this.getLaws();
   });

  }

  getLaws() {
    this.getApiItemSub = this.indexService.getData()
      .subscribe(data => {
        this.legalindexitems = data;
        this.filteredOptions = this.searchCtrl.valueChanges
        .pipe(
          startWith<string | LegalIndexItem>(''),
          map(value => typeof value === 'string' ? value : value.name),
          map(name => name && name.toString().length>2 ? this._filterStatutes(name.toString()) : [])
        );
      });
  }


  openDialogWithTemplateRef(templateRef: TemplateRef<any>) {
    this.dialog.open(templateRef);
  }

  _filterStatutes(val: string) {
    const filterValue = val.toLowerCase();

    return this.legalindexitems.filter(option => option.name.toString().indexOf(filterValue) === 0 || option.year.toString().indexOf(filterValue) === 0);
  }

  displayStatuteFn(item?: LegalIndexItem): string | undefined {
    return item ? new Url2StatutePipe().transform(item._id): undefined;
  }

  navigateTo(item?: LegalIndexItem) {
    if (item) {
      this.router.navigate([`/statute/${item._id}`]);
    }
    return false;
  }

  startTour() {
    // Destroy running tour
    hopscotch.endTour(true);
    // Initialize new tour 
    hopscotch.startTour(this.tourSteps());
  }

  tourSteps(): any {
    // let self = this;
    return {
      id: 'demo-tour',
      showPrevButton: true,
      onEnd: function() {
        // self.snackBar.open('User tour ended!', 'close', { duration: 3000 });
      },
      onClose: function() {
        // self.snackBar.open('You just closed User Tour!', 'close', { duration: 3000 });
      },
      steps: [
        {
          title: 'Step one',
          content: 'This is step description.',
          target: 'areaOne', // Element ID
          placement: 'left',
          xOffset: 10
        },
        {
          title: 'Define your steps',
          content: 'This is step description.',
          target: document.querySelector('#areaOne code'),
          placement: 'left',
          xOffset: 0,
          yOffset: -10
        },
        {
          title: 'Invoke startTour function',
          content: 'This is step description.',
          target: document.querySelector('#areaTwo code'), // Element ID
          placement: 'left',
          xOffset: 15,
          yOffset: -10
        }
      ]
    }
  }


}
