export class CommentModel {
    author_email: string
    author_id: number
    author_name: string
    body: string
    id: number
    likes_dislikes: Array<ReactionsModel>
    parent_id: number
    profile_image: string
    replies: Array<CommentModel>
    unix_timestamp: string
    showReplyForm: boolean

    constructor() {
        this.author_email = null
        this.author_id = null
        this.author_name = null
        this.body = null
        this.id = null
        this.likes_dislikes = []
        this.parent_id = null
        this.profile_image = null
        this.replies = []
        this.unix_timestamp = null
        this.showReplyForm = null
    }
}

export class ReactionsModel {
    type: string
    unix_timestamp: string
    user_id: number
}