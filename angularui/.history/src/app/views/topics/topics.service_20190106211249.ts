import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { DataService } from '../../shared/services';
import {  Topic} from '@app/shared/models/legal.models';

@Injectable()
export class TopicsService {

 constructor(
   private http: HttpClient,
   private dataService: DataService,
  ) {
   }


  getTopics(): Observable<Topic[]> {
         return this.dataService.get<Topic[]>(`${this.dataService.apiUrl}/topics`);

  }

}
