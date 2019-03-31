import { Component, ViewChild ,  OnInit, OnDestroy } from '@angular/core';
import { IndexService } from '../index.service';
import { MatDialogRef, MatDialog, MatSnackBar, MatSidenav } from '@angular/material';
import { AppConfirmService } from '@app/shared/services/app-confirm/app-confirm.service';
import { AppLoaderService } from '@app/shared/services/app-loader/app-loader.service';
import { IndexTablePopupComponent } from './index-table-popup/index-table-popup.component';
import { Subscription, Observable, combineLatest, of } from 'rxjs';
import { egretAnimations } from '@app/shared/animations/egret-animations';
import {DatatableComponent} from '@swimlane/ngx-datatable';
import { LegalIndexItem , Statute } from '@app/shared/models/legal.models';
import { FormGroup, FormBuilder } from '@angular/forms';
import { startWith, debounceTime, switchMap, map } from 'rxjs/operators';
import { isNilOrEmpty } from '@app/shared/helpers/utils';
import { Router } from '@angular/router';
import { routerNgProbeToken } from '@angular/router/src/router_module';

@Component({
  selector: 'app-index-table',
  templateUrl: './index-table.component.html',
  animations: egretAnimations
})
export class IndexTableComponent implements OnInit, OnDestroy {

  public isSideNavOpen: boolean;
  public viewMode: string = 'grid-view';

  @ViewChild(MatSidenav) private sideNav: MatSidenav;
  @ViewChild(DatatableComponent) table: DatatableComponent;

  public activeType: string = '';
  public filterForm: FormGroup;

  //Filters
  public initialFilters = {
    year: 2019,
    minRating: 1,
    maxRating: 5
  };

  // TODO :  move to a Pipe or Prototype Extension
  //range = (start: number, end: number) => Array.from({length: (end - start)} , (v, k) => k + start);

  years = [
    { value: 2007, viewValue: '2007' },
    { value: 2008, viewValue: '2008' },
    { value: 2009, viewValue: '2009' },
    { value: 2010, viewValue: '2010' },
    { value: 2011, viewValue: '2011' },
    { value: 2012, viewValue: '2012' },
    { value: 2013, viewValue: '2013' },
    { value: 2014, viewValue: '2014' },
    { value: 2015, viewValue: '2015' },
    { value: 2016, viewValue: '2016' },
    { value: 2017, viewValue: '2017' },
    { value: 2018, viewValue: '2018' },
    { value: 2019, viewValue: '2019' },
  ];

  public apiitems: Observable<LegalIndexItem[]> ;

  public getApiItemSub: Subscription;
  constructor(
    private dialog: MatDialog,
    private snack: MatSnackBar,
    private indexService: IndexService,
    private confirmService: AppConfirmService,
    private loader: AppLoaderService,
    private fb: FormBuilder,
    private router: Router,
  ) { }

  ngOnInit() {
    this.buildFilterForm(this.initialFilters);
    setTimeout(() => {
      this.loader.open();
    });

    this.apiitems = this.getFilteredData(this.filterForm)
    .pipe(
      map(items => {
        this.loader.close();
        return items;
      })
    );
    
  }

  ngOnDestroy() {
    if (this.getApiItemSub) {
      this.getApiItemSub.unsubscribe();
    }

  }

  buildFilterForm(filterData:any = {}) {
    this.filterForm = this.fb.group({
      search: [''],
      type: [''],
      year: [filterData.year],
      minRating: [filterData.minRating],
      maxRating: [filterData.maxRating]
    });
  }

  setActiveType(type: string) {
    this.activeType = type;
    this.filterForm.controls['type'].setValue(type)
  }

  toggleSideNav() {
    this.sideNav.opened = !this.sideNav.opened;
  }

  public getFilteredData(filterForm: FormGroup): Observable<LegalIndexItem[]> {
    return combineLatest(
      this.indexService.getData(),
      filterForm.valueChanges
      .pipe(
        startWith(this.initialFilters),
        debounceTime(400)
      )
    )
    .pipe(
      switchMap(([items, filterData]) => {
        return this.filterData(items, filterData);
      })
    );

  }
  /*
  * If your data set is too big this may raise performance issue.
  * You should implement server side filtering instead.
  */ 
  private filterData(items: LegalIndexItem[], filterData): Observable<LegalIndexItem[]> {

    let filter_function  = (item: LegalIndexItem) => {
      const type_cond = !isNilOrEmpty(filterData.type) ? item.type === filterData.type : true;
      const year_cond = filterData.year > 0  ? item.year === filterData.year : true;
      const name_cond = !isNilOrEmpty(filterData.search ) ? (item.name).toString().indexOf(filterData.search) > -1 : true;
      return type_cond && year_cond && name_cond;
      };

      // filter our data
      
      let filteredData = items.filter(filter_function);
      // Whenever the filter changes, always go back to the first page
      this.table.offset = 0;
       
    return of(filteredData)
  }

  rowClick(event) {
    if (event.type === 'click') {
      if (event.row && event.row._id) {
        const statute_id = event.row._id;
        this.router.navigate(['/statute' , statute_id]);
      }

    }
}

  openPopUp(e : any, data: any = {}, isNew?) {

    e.stopPropagation();
    e.preventDefault();
    const title = data.name + '/' + data.year; //isNew ? 'Add new member' : 'Update member';
    const dialogRef: MatDialogRef<any> = this.dialog.open(IndexTablePopupComponent, {
      width: '720px',
      disableClose: true,
      data: { title: title, payload: data }
    });
    dialogRef.afterClosed()
      .subscribe(res => {
        if (!res) {
          // If user press cancel
          return false;
        }
        return false;

      });
      return false;
  }
}
