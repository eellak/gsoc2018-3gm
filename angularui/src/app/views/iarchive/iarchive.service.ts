import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { DataService } from '../../shared/services';
import { IaResource ,  IaStatsResource } from '../../shared/models/iarchive.models';

@Injectable()
export class IaService {

 constructor(
   private http: HttpClient,
   private dataService: DataService,
  ) {
   }

  getDataConf() {
    return [
      {
        prop: '_id'
      },
      {
        prop: 'downloads',
        name: 'downloads'
      },
      {
        prop: 'title',
        name: 'Title'
      },
      {
        prop: 'addeddate',
        name: 'Date'
      },
      {
        prop: 'year',
        name: 'Year'
      },
      {
        prop: 'month',
        name: 'Month'
      }
    ];
  }

getAll(year?: number): Observable<any> {
    const year_part = year ? '/' + year.toString() : '';
    return this.dataService.get<Array<IaResource>>(`${this.dataService.apiUrl}/ia/index${year_part}`);
}

getDetails(identifier: string): Observable<IaResource> {

  return this.dataService.get<IaResource>(`${this.dataService.apiUrl}/ia/${identifier}`);

}

getStats(): Observable<IaStatsResource> {

  return this.dataService.get<IaStatsResource>(`${this.dataService.apiUrl}/ia/stats`);

}


}
