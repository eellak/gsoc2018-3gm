import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { AppLoaderService } from '@app/shared/services/app-loader/app-loader.service';
import { StatuteService } from '../statute.service';

import { MatSnackBar  } from '@angular/material';

import {Diff2Html} from 'diff2html';
import { Subscription } from 'rxjs';
import { finalize } from 'rxjs/operators';


@Component({
  selector: 'app-statute-diff',
  templateUrl: './statute-diff.component.html',
  styleUrls: ['./statute-diff.component.css'],
  providers: [StatuteService]
})
export class StatuteDiffComponent implements OnInit {
  initialStatuteID: string;
  finalStatuteID: string;
  diffstr: string;
  outputFormat: string = 'line-by-line';
  stripContextMode: string = 'false';
  outputHtml: string;

  public getDiffSub: Subscription;
  constructor(
    private statuteService: StatuteService,
    private route: ActivatedRoute,
    private snack: MatSnackBar,
    private loader: AppLoaderService,
  ) { }

  ngOnInit() {
    this.initialStatuteID = this.route.snapshot.params['id'];
    this.finalStatuteID = this.route.snapshot.params['amendeeId'];
    this.getDiff();
  }

  getDiff() {

    setTimeout(() => {
      this.loader.open();
    });


    this.getDiffSub =  this.statuteService.getDiffs(this.initialStatuteID, this.finalStatuteID, this.stripContextMode)
    .pipe(
      finalize(() =>  {
      this.loader.close();
    })
    )
    .subscribe(data => {
      this.diffstr = data.join('');
      this.showdiff();
    },
    err => {
    this.snack.open("Πρόβλημα κατά την ανάκτηση δεδομένων!", 'OK', { duration: 4000 });
    }  
    );


  }

  showdiff() {
    const   templates =  {
      'generic-wrapper': '<div class="d2h-wrapper default-bg">{{{content}}}</div>' ,
      'tag-file-renamed': '<span class="d2h-tag d2h-moved d2h-moved-tag icon-chip mat-color-default mat-bg-warn" >ΑΛΛΑΓΕΣ</span>'
    } ;

    const diffparams = {
      inputFormat: 'diff',
      outputFormat: this.outputFormat,
      showFiles: false,
      matching: 'lines',
      rawTemplates: templates
      };

    const outputHtml = Diff2Html.getPrettyHtml(this.diffstr, diffparams);
    this.outputHtml = outputHtml;
  }

}
