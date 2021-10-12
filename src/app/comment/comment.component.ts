import { Component, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import * as moment from 'moment';
import { BackendService } from '../backend.service';
import { ConfirmPopupComponent } from '../confirm-popup/confirm-popup.component';
import { MessageService } from '../message.service';
import { CommentModel } from '../models/commentModel';
import { UserModel } from '../models/userModel';

@Component({
  selector: 'app-comment',
  templateUrl: './comment.component.html',
  styleUrls: ['./comment.component.css']
})
export class CommentComponent implements OnInit {
  @Input() user: UserModel
  @Input() comments: Array<CommentModel>
  @Input() replyLevel: number
  deletingComment: CommentModel
  submittingReaction: CommentModel

  moment: any = moment
  
  constructor(
    public dialog: MatDialog,
    private backendService: BackendService,
    private messageService: MessageService
  ) { }

  ngOnInit(): void {
  }

  getNumReactions(comment: CommentModel, type: string) {
    return comment.likes_dislikes.filter(x => x.type == type).length
  }

  userReacted(comment: CommentModel, type: string) {
    return comment.likes_dislikes.filter(x => 
      this.user?.id == x.user_id &&
      type == x.type
    ).length > 0
  }

  deleteComment(comment: CommentModel) {
    const dialogRef = this.dialog.open(ConfirmPopupComponent, {
      data: { 
        title: "Delete Comment",
        message: "Are you sure you want to delete this comment?<br>(Warning: deleting this comment will also delete all of its replies.)",
        primaryButton: "Confirm"
      }
    })

    dialogRef.afterClosed().subscribe(result => {
      if (result === true) {
        this.deletingComment = comment
        this.backendService.deleteComment(comment.id).toPromise().then(() => {
          this.backendService.fireRefetchComments()
          this.messageService.open("Successfully deleted comment thread.")
        }).catch(error => {
          this.messageService.open("An error occured while trying to delete your comment. Please try again!")
        })
      }
    })
  }

  submitReaction(comment: CommentModel, type: string) {
    this.submittingReaction = comment
    this.backendService.submitReaction(comment.id, this.user.id, type).toPromise().then(() => {
      this.backendService.fireRefetchComments()
      let messsageString: string = type == "like" ? "liked" : (type == "dislike" ? "disliked" : "removed reaction from")
      this.messageService.open(`Successfully ${messsageString} comment.`)
      setTimeout(() => {
        this.submittingReaction = null
      }, 250)
    }).catch(error => {
      this.messageService.open("An error occured while trying to process your reaction request. Please try again!")
      this.submittingReaction = null
    })
  }
}
