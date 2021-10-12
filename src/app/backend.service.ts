import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import { config } from './config';

@Injectable({
  providedIn: 'root'
})
export class BackendService {
  private refetchComments = new Subject<any>();
  constructor(
    private http: HttpClient
  ) { }

  getComments() {
    return this.http.get(config.api_root + '/comments')
  }

  getUser() {
    return this.http.get(config.api_root + '/user')
  }

  submitComment(id: number, author_id: number, body: string, parent_id: number) {
    return this.http.post(config.api_root + '/comment', {
      "id": id,
      "author_id": author_id,
      "body": body,
      "parent_id": parent_id
    })
  }

  fireRefetchComments() {
    this.refetchComments.next()
  }

  get events$ () {
    return this.refetchComments.asObservable()
  }
}
