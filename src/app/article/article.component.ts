import { Component, OnInit } from '@angular/core';
import { BackendService } from '../backend.service';
import { CommentModel } from '../models/commentModel';
import { UserModel } from '../models/userModel';

@Component({
  selector: 'app-article',
  templateUrl: './article.component.html',
  styleUrls: ['./article.component.css']
})
export class ArticleComponent implements OnInit {
  comments: Array<CommentModel> = []
  user: UserModel
  totalComments: number
  constructor(
    private backendService: BackendService
  ) { }

  ngOnInit(): void {
    this.getComments()
    this.backendService.getUser().toPromise().then((data: any) => {
      this.user = data
    })

    this.backendService.events$.subscribe(() => {
      this.getComments()
    })
  }

  getComments() {
    this.backendService.getComments().toPromise().then((data: any) => {
      this.comments = data?.comments
      this.totalComments = data?.total
    })
  }

  scrollToComments() {
    document.getElementById('commentsSection').scrollIntoView({ behavior: 'smooth' })
  }

}
