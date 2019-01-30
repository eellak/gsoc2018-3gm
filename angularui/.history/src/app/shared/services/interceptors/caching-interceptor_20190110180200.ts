// #docplaster
import { Injectable } from '@angular/core';
import {
  HttpEvent, HttpHeaders, HttpRequest, HttpResponse,
  HttpInterceptor, HttpHandler
} from '@angular/common/http';

import { Observable, of } from 'rxjs';
import { startWith, tap, switchMap, catchError } from 'rxjs/operators';

import { RequestCache } from '../cache.service';
import { isNil } from '@app/shared/helpers/utils';



/**
 * If request is cachable (e.g., package search) and
 * response is in cache return the cached response as observable.
 * If has 'x-refresh' header that is true,
 * then also re-run the package search, using response from next(),
 * returning an observable that emits the cached response first.
 *
 * If not in cache or not cachable,
 * pass request through to next()
 */

@Injectable()
export class CachingInterceptor implements HttpInterceptor {
  constructor(private cache: RequestCache) {}

  intercept(req: HttpRequest<any>, next: HttpHandler) {
    // continue if not cachable.
    if (!isCachable(req)) { return next.handle(req); }


  const cachedResponse =   this.cache.get(req);

  return cachedResponse.pipe(
     switchMap(value => {

   if (req.headers.get('x-refresh')) {
     const results$ = sendRequest(req, next, this.cache);
     return value ?
       results$.pipe( startWith(value) ) :
       results$;
   }

   if  (value === undefined || isNil(value) || value.status !== 200)
   { return  sendRequest(req, next, this.cache) ; } else { return   of(value); }

   }),
  );

  }
}


/** Is this request cachable? */
function isCachable(req: HttpRequest<any>) {
  // Only GET requests are cachable
  return req.method === 'GET' &&
    // Only npm package search is cachable in this app
     ( req.url.endsWith('/123index123') || req.url.endsWith('/stats') );
}

// #send-request
/**
 * Get server response observable by sending request to `next()`.
 * Will add the response to the cache on the way out.
 */
function sendRequest(
  req: HttpRequest<any>,
  next: HttpHandler,
  cache: RequestCache): Observable<HttpEvent<any>> {

  // No headers allowed in npm search request
  const noHeaderReq = req.clone({ headers: new HttpHeaders() });

  return next.handle(noHeaderReq).pipe(
    tap(event => {
      // There may be other events besides the response.
      // check https://stackoverflow.com/questions/47016104/can-someone-explain-how-this-http-status-code-is-processed
      if (event instanceof HttpResponse && (event.status >= 200 && event.status <= 300 )) {
        cache.put(req, event); // Update the cache.
      }
    })
  );
}
// #end send-request
