import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { DataService } from '../../shared/services';
import { Statute, Article  , StatuteHistoryItem, StatuteLinks, Topic} from '@app/shared/models/legal.models';
import { isNil } from '@app/shared/helpers/utils';

@Injectable()
export class StatuteService {

 constructor(
   private http: HttpClient,
   private dataService: DataService,
  ) {
   }


  getStatuteDetails(statuteID:string): Observable<Statute> {
    return this.dataService.get<Statute>(`${this.dataService.apiUrl}/statute/${statuteID}`);
  }

  getStatuteCodified(statuteID:string):Observable<string> {
    return this.dataService.get<string>(`${this.dataService.apiUrl}/statute/${statuteID}/codified`);
   }

  getStatuteHistory(statuteID: string): Observable<StatuteHistoryItem[]> {
    return this.dataService.get<StatuteHistoryItem[]>(`${this.dataService.apiUrl}/statute/${statuteID}/history`);
  }

  getDiffs(initialStatuteID: string, finalStatuteID: string, stripcontext: string = null): Observable<string[]> {
    return this.dataService.get<string[]>(`${this.dataService.apiUrl}/statute/diff/${initialStatuteID}/${finalStatuteID}`,{stripcontext:stripcontext});
  }

  getLinks(statuteID: string): Observable<StatuteLinks> {
    return this.dataService.get<StatuteLinks>(`${this.dataService.apiUrl}/statute/${statuteID}/links`);
  }


  getStatuteArticles(statuteID: string , articleID?: string): Observable<Article> {

    if (isNil(articleID))
      return this.dataService.get<Article>(`${this.dataService.apiUrl}/statute/${statuteID}/articles`);
    else
        return this.dataService.get<Article>(`${this.dataService.apiUrl}/statute/${statuteID}/articles/${articleID}`);

  }

  getStatuteTopics(statuteID: string): Observable<Topic> {
         return this.dataService.get<Topic>(`${this.dataService.apiUrl}/statute/${statuteID}/topics`);

  }

}
