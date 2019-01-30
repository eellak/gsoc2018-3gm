import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { DataService } from '../../shared/services';
import { StatuteStatsResource  } from '@app/shared/models/legal.models';

@Injectable()
export class DashboardService {

  constructor( private dataService: DataService) { }

  getStats(): Observable<StatuteStatsResource> {
    return this.dataService.get<StatuteStatsResource>(`${this.dataService.apiUrl}/statute/stats`);
  }
}
