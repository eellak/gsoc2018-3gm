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
  constructor(
    private route: ActivatedRoute,
    private statuteService: StatuteService
    ) { }

  ngOnInit() {
    this.statuteID = this.route.snapshot.params['id'];
    this.activeView = this.route.snapshot.params['view'];

  }

}
