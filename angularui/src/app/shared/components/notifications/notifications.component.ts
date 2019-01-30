import { Component, OnInit, ViewChild, Input } from '@angular/core';
import { MatSidenav } from '@angular/material';
import { Router, NavigationEnd } from '@angular/router';

@Component({
  selector: 'app-notifications',
  templateUrl: './notifications.component.html'
})
export class NotificationsComponent implements OnInit {
  @Input() notificPanel;

  // Dummy notifications
  notifications = [{
    message: 'ΦΕΚ 2257/2018 added',
    icon: 'chat',
    time: '1 min ago',
    route: '/',
    color: 'primary'
  }, {
    message: 'ΦΕΚ 2257/2018 added',
    icon: 'chat',
    time: '4 min ago',
    route: '/',
    color: 'accent'
  }, {
    message: 'Server rebooted',
    icon: 'settings_backup_restore',
    time: '12 min ago',
    route: '/charts',
    color: 'warn'
  }]

  constructor(private router: Router) {}

  ngOnInit() {
    this.router.events.subscribe((routeChange) => {
        if (routeChange instanceof NavigationEnd) {
          this.notificPanel.close();
        }
    });
  }
  clearAll(e) {
    e.preventDefault();
    this.notifications = [];
  }
}
