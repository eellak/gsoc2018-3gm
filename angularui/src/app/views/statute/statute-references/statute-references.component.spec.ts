import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { StatuteReferencesComponent } from './statute-references.component';

describe('StatuteReferencesComponent', () => {
  let component: StatuteReferencesComponent;
  let fixture: ComponentFixture<StatuteReferencesComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ StatuteReferencesComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(StatuteReferencesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
