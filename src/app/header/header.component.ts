import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { BackendService } from '../backend.service';
import { config } from '../config';
import { ConfirmPopupComponent } from '../confirm-popup/confirm-popup.component';
import { UserModel } from '../models/userModel';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent implements OnInit {
  user: UserModel
  constructor(
    private backendService: BackendService,
    public dialog: MatDialog,
  ) { }

  ngOnInit(): void {
    this.backendService.getUser().toPromise().then((data: any) => {
      this.user = data
    })
  }

  signOut() {
    const dialogRef = this.dialog.open(ConfirmPopupComponent, {
      data: { 
        title: "Sign Out",
        message: `Are you sure you want to sign out?<br>(Signed in as ${this.user.email}).`,
        primaryButton: "Confirm"
      }
    })

    dialogRef.afterClosed().subscribe(result => {
      if (result === true) {
        window.location.href = config.api_root + '/logout'
      }
    })
  }

  signIn() {
    window.location.href = config.api_root + '/login'
  }

}
