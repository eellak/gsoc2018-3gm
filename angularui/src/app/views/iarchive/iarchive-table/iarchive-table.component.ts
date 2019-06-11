import { Component, OnInit } from '@angular/core';
import { IaService } from '../iarchive.service';

@Component({
  selector: 'app-iarchive-table',
  templateUrl: './iarchive-table.component.html',
  styleUrls: ['./iarchive-table.component.css'],
  providers: [IaService]
})
export class IarchiveTableComponent implements OnInit {
  rows = [];
  columns = [];
  temp = [];

  constructor(private iaservice: IaService) { }

  ngOnInit() {
    this.columns = this.iaservice.getDataConf();
     this.iaservice.getAll().subscribe((res) =>  {
      this.rows = this.temp = res;
    });
  }

  updateFilter(event) {
    const val = event.target.value.toLowerCase();
    const columns = Object.keys(this.temp[0]);
    // Removes last "$$index" from "column"
    columns.splice(columns.length - 1);

    // console.log(columns);
    // tslint:disable-next-line:curly
    if (!columns.length) return;

    const rows = this.temp.filter(function(d) {
      for (let i = 0; i <= columns.length; i++) {
        const column = columns[i];
        // console.log(d[column]);
        if (d[column] && d[column].toString().toLowerCase().indexOf(val) > -1) {
          return true;
        }
      }
    });

    this.rows = rows;

  }

}
