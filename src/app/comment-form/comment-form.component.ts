import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { BackendService } from '../backend.service';
import { config } from '../config';
import { ConfirmPopupComponent } from '../confirm-popup/confirm-popup.component';
import { MessageService } from '../message.service';
import { CommentModel } from '../models/commentModel';
import { UserModel } from '../models/userModel';

@Component({
  selector: 'app-comment-form',
  templateUrl: './comment-form.component.html',
  styleUrls: ['./comment-form.component.css']
})
export class CommentFormComponent implements OnInit {
  @Input() user: UserModel
  @Input() comment: CommentModel = new CommentModel()

  submitting: boolean = false
  commentForm: FormGroup
  constructor(
    private fb: FormBuilder,
    private backendService: BackendService,
    private messageService: MessageService,
    public dialog: MatDialog,
  ) { }

  ngOnInit(): void {
    this.commentForm = this.fb.group({
      body: [null]
    })
  }

  submitComment() {
    this.submitting = true
    this.backendService.submitComment(
      null,
      this.user.id,
      this.commentForm.controls['body'].value.trim(),
      this.comment.id
    ).toPromise().then((data: any) => {
      this.backendService.fireRefetchComments()
      this.submitting = false
      this.messageService.open("Successfully submitted comment.")
      this.commentForm.reset()
    }).catch(error => {
      this.submitting = false
      this.messageService.open("There was an error submitted your comment. Please try again.")
    })
  }

  signIn() {
    window.location.href = config.api_root + '/login'
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

}
