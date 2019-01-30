import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import {throwError as observableThrowError } from 'rxjs';
import { delay } from 'rxjs/operators';
import { DataService } from '../../shared/services';
import { LegalIndexItem } from '@app/shared/models/legal.models';

@Injectable()
export class IndexService {
  items: any[];

  constructor(
    private http: HttpClient,
    private dataService: DataService,
  ) {
    // this.items = ...
  }

  getData(): Observable<LegalIndexItem[]> {
    return this.dataService.get<Array<LegalIndexItem>>(`${this.dataService.apiUrl}/statute/index`);
}




}
