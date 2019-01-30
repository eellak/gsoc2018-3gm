import { Injectable } from '@angular/core';
import { HttpRequest, HttpResponse } from '@angular/common/http';
import { RequestCache,  RequestCacheWithMap ,  RequestCacheEntry } from './request-cache.service';

import { LocalStorage } from '@ngx-pwa/local-storage';
import { mergeMap, filter, switchMap, map } from 'rxjs/operators';
import { from, Observable, of } from 'rxjs';
import { HttpClient } from 'selenium-webdriver/http';



const maxAge = 300000; // maximum cache age (ms)  5min

/*
LocalStorage Implementation

*/
@Injectable()
export class RequestCacheWithLocalStorage implements RequestCache {

  constructor(
    protected storagecache: LocalStorage,
    protected memorycache: RequestCacheWithMap) {}

  getAsync(req: HttpRequest<any>): Observable< HttpResponse<any> | undefined > {

    const url = req.urlWithParams;
     // Angular HttpClient

    const cachedResponse = this.memorycache.get(req);

    // storageService.read wraps AsyncLocalStorage.getItem
    const readFromStorage$ = this.storagecache.getUnsafeItem<RequestCacheEntry>(url)
    .pipe(
      switchMap((x) => (x.lastRead < (Date.now() - maxAge)) ? undefined :  of(x.response))
    );

       return of(cachedResponse)
      .pipe(switchMap((value) => value && of(value) || readFromStorage$ ));
}


  putAsync(req: HttpRequest<any>, response: HttpResponse<any>): void {
    const url = req.urlWithParams;
    console.log(`Caching response from "${url}".`);

    if (response.body) {
      const entry = { url, response, lastRead: Date.now() };
      this.memorycache.put(req, response);
      this.storagecache.setItem(url, entry).subscribe(() => {
        console.log('response cached [ok]');
      });
    }
    // remove expired cache entries
    const expired = Date.now() - maxAge;
    this.storagecache.keys().pipe(
      mergeMap((keys) => from(keys)),
      switchMap((key) =>  this.storagecache.getUnsafeItem<RequestCacheEntry>(key)),
      filter((item) => item.lastRead < expired), /* filter expired */
      mergeMap((item) => this.storagecache.removeItem(item.url))  /* Remove the item for each key */
    ).subscribe({ complete: () => {
       // we want to act only when all the operations are done */
      console.log('Done!');
    } });

    console.log(`Request cache size: ${this.storagecache.size}.`);
  }
}
