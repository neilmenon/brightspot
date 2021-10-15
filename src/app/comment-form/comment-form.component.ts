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
  @Input() isReply: boolean

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

    if (!this.isReply) {
      this.commentForm.controls['body'].patchValue(this.comment.body)
    }
  }

  submitComment() {
    this.submitting = true
    this.backendService.submitComment(
      this.isReply ? null : this.comment.id,
      this.user.id,
      this.commentForm.controls['body'].value.trim(),
      this.isReply ? this.comment.id : this.comment.parent_id
    ).toPromise().then((data: any) => {
      this.backendService.fireRefetchComments()
      this.submitting = false
      let submitType: string = this.comment.id && !this.isReply ? 'updated' : 'submitted'
      this.messageService.open(`Successfully ${submitType} comment.`)
      this.commentForm.reset()
    }).catch(error => {
      this.submitting = false
      this.messageService.open("There was an error submitting your comment. Please try again.")
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
