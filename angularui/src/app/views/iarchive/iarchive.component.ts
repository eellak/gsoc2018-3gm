import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { IaService } from './iarchive.service';
import { IaStatsResource } from '@app/shared/models/iarchive.models';

@Component({
  selector: 'app-iarchive',
  templateUrl: './iarchive.component.html',
  styleUrls: ['./iarchive.component.css'],
  providers: [IaService]
})
export class IarchiveComponent implements OnInit {
  activeView: string = 'overview';
  stats: IaStatsResource = {
    res_count_lastyear: 0,
    res_count_lastmonth: 0 ,
    res_count_lastweek: 0 ,
    res_count_total: 0 ,
    res_last_docs : [] } ;

  // Doughnut
  doughnutChartColors: any[] = [{
    backgroundColor: ['#fff', 'rgba(0, 0, 0, .24)',]
  }];

  total1: number = 500;
  data1: number = 200;
  doughnutChartData1: number[] = [this.data1, (this.total1 - this.data1)];

  total2: number = 1000;
  data2: number = 400;
  doughnutChartData2: number[] = [this.data2, (this.total2 - this.data2)];

  doughnutChartType = 'doughnut';
  doughnutOptions: any = {
    cutoutPercentage: 85,
    responsive: true,
    maintainAspectRatio: true,
    legend: {
      display: false,
      position: 'bottom'
    },
    elements: {
      arc: {
        borderWidth: 0,
      }
    },
    tooltips: {
      enabled: false
    }
  };

  constructor(
    private router: ActivatedRoute,
    private iaservice: IaService
    ) { }

  ngOnInit() {
    this.activeView = this.router.snapshot.params['view'];
    this.iaservice.getStats().subscribe((res) =>  {
       this.stats = res;
    });
  }

}
