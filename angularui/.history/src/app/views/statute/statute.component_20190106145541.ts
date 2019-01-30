import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { StatuteService } from './statute.service';

@Component({
  selector: 'app-statute',
  templateUrl: './statute.component.html',
  styleUrls: ['./statute.component.css'],
  providers: [StatuteService]
})
export class StatuteComponent implements OnInit {
  activeView: string = 'codified';
  isSidenavOpen: Boolean = true;
  statuteID: string;
  ranking:number = -1;

  constructor(
    private route: ActivatedRoute,
    private statuteService: StatuteService
    ) { }

  ngOnInit() {
    this.statuteID = this.route.snapshot.params['id'];
    this.activeView = this.route.snapshot.params['view'];

  }

  
  getStatuteRanking() {
    this.statuteService.getStatuteRanking(this.statuteID)
    .subscribe(data => {
      this.ranking = data;
    }
    );
  }

}
