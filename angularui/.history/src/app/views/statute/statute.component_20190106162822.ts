import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { StatuteService } from './statute.service';
import { IndexService } from '../indexes/index.service';
import { LegalIndexItem } from '@app/shared/models/legal.models';

@Component({
  selector: 'app-statute',
  templateUrl: './statute.component.html',
  styleUrls: ['./statute.component.css'],
  providers: [StatuteService, IndexService]
})
export class StatuteComponent implements OnInit {
  activeView: string = 'codified';
  isSidenavOpen: Boolean = true;
  statuteID: string;
  ranking:number = -1;

  constructor(
    private route: ActivatedRoute,
    private statuteService: StatuteService,
    private indexService: IndexService
    ) { }

  ngOnInit() {
    this.statuteID = this.route.snapshot.params['id'];
    this.activeView = this.route.snapshot.params['view'];
    this.getStatuteRanking();
    this.getStatuteRanking2();
  }

  
  getStatuteRanking() {
    console.time('load_ranking');
    this.statuteService.getStatuteRanking(this.statuteID)
    .subscribe(data => {
      this.ranking = data;
      console.timeEnd('load_ranking');
    }
    );
  }

  getStatuteRanking2() {
    console.time('load_ranking2');
    this.indexService.getData()
    .subscribe(data => {
      const index:LegalIndexItem[] = data;
      const item = (index.find(item => item._id==this.statuteID));
      this.ranking = (item)?item.rank:-1;
      console.timeEnd('load_ranking2');
    }
    );
  }


}
