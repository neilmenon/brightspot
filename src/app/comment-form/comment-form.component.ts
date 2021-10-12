import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { BackendService } from '../backend.service';
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
    private messageService: MessageService
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

}
