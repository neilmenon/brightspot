import { Component, Input, OnInit } from '@angular/core';
import * as moment from 'moment';
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

  moment: any = moment
  
  constructor() { }

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
}
