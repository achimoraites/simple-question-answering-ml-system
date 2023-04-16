provider "aws" {
  region = "us-west-2"
}

locals {
  project_name = "simple-qa-system"
}

resource "aws_ecs_cluster" "this" {
  name = local.project_name
}

resource "aws_ecs_task_definition" "this" {
  family                   = local.project_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([
    {
      name      = "flask_app"
      image     = "your_flask_app_image"
      essential = true
      portMappings = [
        {
          containerPort = 5000
          hostPort      = 5001
        }
      ],
      links = ["elasticsearch"]
    },
    {
      name      = "elasticsearch"
      image     = "docker.elastic.co/elasticsearch/elasticsearch:7.16.3"
      essential = true
      portMappings = [
        {
          containerPort = 9200
          hostPort      = 9200
        },
        {
          containerPort = 9300
          hostPort      = 9300
        }
      ],
      environment = [
        {
          name  = "discovery.type"
          value = "single-node"
        },
        {
          name  = "bootstrap.memory_lock"
          value = "true"
        },
        {
          name  = "ES_JAVA_OPTS"
          value = "-Xms512m -Xmx512m"
        }
      ],
      mountPoints = [
        {
          sourceVolume  = "esdata"
          containerPath = "/usr/share/elasticsearch/data"
        }
      ]
    },
    {
      name      = "kibana"
      image     = "docker.elastic.co/kibana/kibana:7.16.3"
      essential = true
      portMappings = [
        {
          containerPort = 5601
          hostPort      = 5601
        }
      ],
      links = ["elasticsearch"]
    }
  ])
}

resource "aws_iam_role" "ecs_execution_role" {
  name = "${local.project_name}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role" "ecs_task_role" {
  name = "${local.project_name}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
  role       = aws_iam_role.ecs_execution_role.name
}

resource "aws_security_group" "ecs_security_group" {
  name        = "${local.project_name}-ecs-sg"
  description = "ECS security group"

  ingress {
    from_port   = 5001
    to_port     = 5001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_vpc" "this" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = local.project_name
  }
}

resource "aws_subnet" "this" {
  cidr_block = "10.0.1.0/24"
  vpc_id     = aws_vpc.this.id

  tags = {
    Name = "${local.project_name}-subnet"
  }
}

resource "aws_ecs_service" "this" {
  name            = local.project_name
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.this.id]
    security_groups  = [aws_security_group.ecs_security_group.id]
    assign_public_ip = true
  }
}
