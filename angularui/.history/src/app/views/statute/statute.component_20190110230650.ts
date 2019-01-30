import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { StatuteService } from './statute.service';
import { IndexService } from '../indexes/index.service';
import { LegalIndexItem, Statute } from '@app/shared/models/legal.models';

@Component({
  selector: 'app-statute',
  templateUrl: './statute.component.html',
  styleUrls: ['./statute.component.css'],
  providers: [StatuteService, IndexService]
})
export class StatuteComponent implements OnInit {
  activeView = 'codified';
  isSidenavOpen: Boolean = true;
  statuteID: string;
  ranking = -1;
  archive = '';
  statute: Statute;

  constructor(
    private route: ActivatedRoute,
    private statuteService: StatuteService,
    ) { }

  ngOnInit() {
    this.statuteID = this.route.snapshot.params['id'];
    this.activeView = this.route.snapshot.params['view'];
    this.getStatuteDetails();
  }

  getStatuteDetails() {
    this.statuteService.getStatuteDetails(this.statuteID)
    .subscribe(data => {
      this.statute = data;
      this.archive = this.statute.archive;
      this.ranking = this.statute.rank;
    }
    );
  }
 


}
